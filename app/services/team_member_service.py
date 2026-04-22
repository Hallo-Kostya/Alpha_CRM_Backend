from uuid import UUID
from fastapi import Depends, HTTPException, status
from typing import List, Optional

from app.schemas.team_member import TeamMember, TeamMemberCreate, TeamMemberUpdate, TeamMemberWithTeamInfo
from app.infrastructure.database.models.teams.team_member import TeamMemberModel
from app.infrastructure.database.repositories.team_member_repository import (
    TeamMemberRepository,
    team_member_repository_getter,
)
from app.infrastructure.database.repositories.team_repository import (
    TeamRepository,
    team_repository_getter,
)
from app.infrastructure.database.repositories.student_repository import (
    StudentRepository,
    student_repository_getter,
)
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class TeamMemberService:
    """Application service for team members."""

    def __init__(
        self,
        team_member_repo: TeamMemberRepository,
        team_repo: TeamRepository,
        student_repo: StudentRepository,
    ):
        self._team_repo = team_repo
        self._student_repo = student_repo
        self._team_member_repo = team_member_repo

    def _to_orm(self, scheme: TeamMemberCreate) -> TeamMemberModel:
        """Convert schema to ORM model."""
        return TeamMemberModel(**scheme.model_dump(exclude_unset=True))
    
    def _to_schema(self, orm_model: TeamMemberModel) -> TeamMember:
        """Convert ORM model to schema."""
        return TeamMember.model_validate(orm_model, from_attributes=True)

    async def _validate_team_and_student_exist(
        self, team_id: UUID, student_id: UUID
    ) -> None:
        """Check team and student existence."""
        team = await self._team_repo.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team with ID {team_id} not found"
            )

        student = await self._student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID {student_id} not found"
            )

    async def add_student_to_team(self, team_id: UUID, student_id: UUID, role: Optional[str] = None, study_group: Optional[str] = None) -> TeamMember:
        """Привязать студента к команде с указанием роли и группы."""
        await self._validate_team_and_student_exist(team_id, student_id)

        existing = await self._team_member_repo.get_by_team_and_student(team_id, student_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Студент уже состоит в этой команде"
            )

        # Создаем связь
        team_member_data = {
            "team_id": team_id,
            "student_id": student_id,
            "role": role,
            "study_group": study_group
        }
        
        orm_obj = TeamMemberModel(**team_member_data)
        created_obj = await self._team_member_repo.create(orm_obj)
        return self._to_schema(created_obj)

    async def update_student_role_and_group(self, team_id: UUID, student_id: UUID, role: Optional[str] = None, study_group: Optional[str] = None) -> Optional[TeamMember]:
        """Обновить роль и группу студента в команде."""
        # Находим связь студент-команда
        team_member = await self._team_member_repo.get_by_team_and_student(team_id, student_id)
        if not team_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Студент не найден в этой команде"
            )

        # Обновляем только переданные поля
        update_data = {}
        if role is not None:
            update_data["role"] = role
        if study_group is not None:
            update_data["study_group"] = study_group

        if update_data:
            updated_obj = await self._team_member_repo.update(team_member, update_data)
            return self._to_schema(updated_obj)
        
        return self._to_schema(team_member)

    async def remove_student_from_team(self, team_id: UUID, student_id: UUID) -> bool:
        """Удалить студента из команды."""
        # Проверяем, что связь существует
        team_member = await self._team_member_repo.get_by_team_and_student(team_id, student_id)
        if not team_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Студент не найден в этой команде"
            )

        # Удаляем связь
        deleted = await self._team_member_repo.delete_by_team_and_student(team_id, student_id)
        return deleted

    async def get_by_id(self, team_id: UUID, student_id: UUID) -> TeamMember | None:
        """Get team member by team and student IDs."""
        team_member = await self._team_member_repo.get_by_team_and_student(team_id, student_id)
        if not team_member:
            return None
        return self._to_schema(team_member)


    async def get_student_teams(self, student_id: UUID) -> List[TeamMember]:
        """Get all teams of student."""
        student = await self._student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID {student_id} not found"
            )

        student_teams = await self._team_member_repo.get_by_student_id(student_id)
        return [self._to_schema(team_member) for team_member in student_teams]

    async def get_student_teams_with_info(self, student_id: UUID) -> List[TeamMemberWithTeamInfo]:
        """Get all teams of student with team information."""
        # Check student existence
        student = await self._student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID {student_id} not found"
            )

        # Get links with eager loaded team info
        query = (
            select(TeamMemberModel)
            .where(TeamMemberModel.student_id == student_id)
            .options(selectinload(TeamMemberModel.team))
        )
        
        result = await self._team_member_repo.session.execute(query)
        team_members = result.scalars().all()
        
        # Transform to DTO with team information
        return [
            TeamMemberWithTeamInfo(
                team_id=UUID(str(tm.team_id)),
                student_id=UUID(str(tm.student_id)),
                role=tm.role,
                study_group=tm.study_group,
                team_name=tm.team.name if tm.team else "Unknown team",
                team_group_link=tm.team.group_link if tm.team else None
            )
            for tm in team_members
        ]



def team_member_service_getter(
    team_member_repo: TeamMemberRepository = Depends(team_member_repository_getter),
    team_repo: TeamRepository = Depends(team_repository_getter),
    student_repo: StudentRepository = Depends(student_repository_getter),
) -> TeamMemberService:
    return TeamMemberService(team_member_repo, team_repo, student_repo)
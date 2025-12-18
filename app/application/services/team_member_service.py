from uuid import UUID
from fastapi import Depends, HTTPException, status
from typing import List, Optional

from app.application.services.base_service import BaseService
from app.application.dto.team_member import (
    TeamMemberCreate,
    TeamMemberUpdate
)
from app.domain.entities.teams.team_member import TeamMember
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
from app.application.dto.team_member import TeamMemberWithTeamInfo
from sqlalchemy import select
from sqlalchemy.orm import selectinload

class TeamMemberService(BaseService[TeamMemberModel, TeamMember]):
    orm_model = TeamMemberModel
    pyd_scheme = TeamMember

    def __init__(
        self,
        team_member_repo: TeamMemberRepository,
        team_repo: TeamRepository,
        student_repo: StudentRepository,
    ):
        super().__init__(team_member_repo)
        self._team_repo = team_repo
        self._student_repo = student_repo
        self._team_member_repo = team_member_repo

    async def _validate_team_and_student_exist(
        self, team_id: UUID, student_id: UUID
    ) -> None:
        """Проверить существование команды и студента"""
        team = await self._team_repo.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Команда с ID {team_id} не найдена"
            )

        student = await self._student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Студент с ID {student_id} не найден"
            )

    async def add_student_to_team(
        self, team_id: UUID, data: TeamMemberCreate
    ) -> TeamMember:
        """Добавить студента в команду"""
        await self._validate_team_and_student_exist(team_id, data.student_id)

        existing = await self._team_member_repo.get_by_team_and_student(team_id, data.student_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Студент уже состоит в этой команде"
            )

        # Создаем связь
        team_member_data = {
            "team_id": team_id,
            "student_id": data.student_id,
            "role": data.role,
            "study_group": data.study_group
        }
        
        orm_obj = TeamMemberModel(**team_member_data)
        created_obj = await self._repo.create(orm_obj)
        return self._to_schema(created_obj)

    async def get_team_members(self, team_id: UUID) -> List[TeamMember]:
        """Получить всех студентов команды"""
        team = await self._team_repo.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Команда с ID {team_id} не найдена"
            )

        team_members = await self._team_member_repo.get_by_team_id(team_id)
        return [self._to_schema(member) for member in team_members]

    async def get_student_teams(self, student_id: UUID) -> List[TeamMember]:
        """Получить все команды студента"""
        student = await self._student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Студент с ID {student_id} не найден"
            )

        student_teams = await self._team_member_repo.get_by_student_id(student_id)
        return [self._to_schema(team_member) for team_member in student_teams]

    async def update_team_member(
        self, team_id: UUID, student_id: UUID, data: TeamMemberUpdate
    ) -> Optional[TeamMember]:
        """Обновить данные связи (роль, учебная группа)"""
        team_member = await self._team_member_repo.get_by_team_and_student(team_id, student_id)
        if not team_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Связь между командой и студентом не найдена"
            )

        update_data = data.model_dump(exclude_unset=True)
        updated_obj = await self._repo.update(team_member, update_data)
        return self._to_schema(updated_obj)

    async def remove_student_from_team(
        self, team_id: UUID, student_id: UUID
    ) -> bool:
        """Удалить студента из команды"""
        team_member = await self._team_member_repo.get_by_team_and_student(team_id, student_id)
        if not team_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Связь между командой и студентом не найдена"
            )

        deleted = await self._team_member_repo.delete_by_team_and_student(team_id, student_id)
        return deleted
    

    async def get_student_teams_with_info(self, student_id: UUID) -> List[TeamMemberWithTeamInfo]:
        """Получить все команды студента с информацией о командах"""
        # Проверяем существование студента
        student = await self._student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Студент с ID {student_id} не найден"
            )

        # Получаем связи с предзагрузкой информации о командах
        query = (
            select(TeamMemberModel)
            .where(TeamMemberModel.student_id == student_id)
            .options(selectinload(TeamMemberModel.team))
        )
        
        result = await self._team_member_repo.session.execute(query)
        team_members = result.scalars().all()
        
        # Преобразуем в DTO с информацией о командах
        return [
            TeamMemberWithTeamInfo(
                team_id=UUID(str(tm.team_id)),
                student_id=UUID(str(tm.student_id)),
                role=tm.role,
                study_group=tm.study_group,
                team_name=tm.team.name if tm.team else "Неизвестная команда",
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
from uuid import UUID
from fastapi import Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.application.services.base_service import BaseService
from app.application.dto.project_team import (
    ProjectTeamCreate,
    ProjectTeamUpdate,
    ProjectTeamResponse,
    ProjectTeamWithInfo,
)
from app.infrastructure.database.models.projects.project_team import ProjectTeamModel
from app.infrastructure.database.repositories.project_team_repository import (
    ProjectTeamRepository,
    project_team_repository_getter,
)
from app.infrastructure.database.repositories.project_repository import (
    ProjectRepository,
    project_repository_getter,
)
from app.infrastructure.database.repositories.team_repository import (
    TeamRepository,
    team_repository_getter,
)
from app.domain.enums.project_team_status import ProjectTeamStatus


class ProjectTeamService(BaseService[ProjectTeamModel, ProjectTeamResponse]):
    orm_model = ProjectTeamModel
    pyd_scheme = ProjectTeamResponse

    def __init__(
        self,
        project_team_repo: ProjectTeamRepository,
        project_repo: ProjectRepository,
        team_repo: TeamRepository,
    ):
        super().__init__(project_team_repo)
        self._project_team_repo = project_team_repo
        self._project_repo = project_repo
        self._team_repo = team_repo

    async def _validate_project_and_team_exist(
        self, project_id: UUID, team_id: UUID
    ) -> None:
        """Проверить существование проекта и команды"""
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Проект с ID {project_id} не найден"
            )

        team = await self._team_repo.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Команда с ID {team_id} не найдена"
            )

    async def assign_team_to_project(
        self, project_id: UUID, data: ProjectTeamCreate
    ) -> ProjectTeamResponse:
        """Назначить команду на проект"""
        # Проверяем существование проекта и команды
        await self._validate_project_and_team_exist(project_id, data.team_id)

        # Получаем информацию о проекте для проверок
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Проект с ID {project_id} не найден"
            )
        
        # Проверяем, что у проекта есть year и semester
        if not hasattr(project, 'year') or not hasattr(project, 'semester'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Проект не имеет указанных года и семестра"
            )
        
        # Проверяем, не назначена ли команда уже на этот проект
        existing = await self._project_team_repo.get_by_project_and_team(
            project_id, data.team_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Команда уже назначена на этот проект"
            )

        # Проверяем, что у команды нет другого активного проекта в том же семестре
        active_project = await self._project_team_repo.get_active_project_for_team_in_semester(
            data.team_id, project.year, project.semester
        )
        if active_project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Команда уже участвует в проекте {active_project.project_id} "
                      f"в {project.year} {project.semester.value} семестре"
            )

        # Создаем связь
        project_team_data = {
            "project_id": project_id,
            "team_id": data.team_id,
            "status": data.status
        }
        
        orm_obj = ProjectTeamModel(**project_team_data)
        created_obj = await self._repo.create(orm_obj)
        return self._to_schema(created_obj)

    async def get_project_teams(
        self, project_id: UUID, project_team_status: Optional[ProjectTeamStatus] = None
    ) -> List[ProjectTeamResponse]:
        """Получить все команды проекта"""
        # Проверяем существование проекта
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Проект с ID {project_id} не найден"
            )

        project_teams = await self._project_team_repo.get_by_project_id(
            project_id, project_team_status
        )
        return [self._to_schema(team) for team in project_teams]

    async def get_team_projects(
        self, team_id: UUID, project_team_status: Optional[ProjectTeamStatus] = None
    ) -> List[ProjectTeamResponse]:
        """Получить все проекты команды"""
        # Проверяем существование команды
        team = await self._team_repo.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Команда с ID {team_id} не найдена"
            )

        team_projects = await self._project_team_repo.get_by_team_id(
            team_id, project_team_status
        )
        return [self._to_schema(project_team) for project_team in team_projects]

    async def get_current_team_project(
        self, team_id: UUID
    ) -> Optional[ProjectTeamResponse]:
        """Получить текущий активный проект команды"""
        # Получаем команду
        team = await self._team_repo.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Команда с ID {team_id} не найдена"
            )
        
        # Находим активные связи команды
        active_links = await self._project_team_repo.get_by_team_id(
            team_id, ProjectTeamStatus.ACTIVE
        )
        
        # Возвращаем первую активную связь (должна быть только одна по бизнес-правилам)
        if active_links:
            return self._to_schema(active_links[0])
        return None

    async def get_project_teams_with_info(
        self, project_id: UUID
    ) -> List[ProjectTeamWithInfo]:
        """Получить команды проекта с детальной информацией"""
        # Проверяем существование проекта
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Проект с ID {project_id} не найден"
            )

        # Получаем связи с предзагрузкой информации о командах
        query = (
            select(ProjectTeamModel)
            .where(ProjectTeamModel.project_id == project_id)
            .options(selectinload(ProjectTeamModel.team))
        )
        
        result = await self._project_team_repo.session.execute(query)
        project_teams = result.scalars().all()
        
        # Преобразуем в DTO с информацией
        result_list = []
        for pt in project_teams:
        # Передаем project.semester как есть - валидатор в DTO обработает конвертацию
            result_list.append(
                ProjectTeamWithInfo(
                    project_id=UUID(str(pt.project_id)),
                    team_id=UUID(str(pt.team_id)),
                    assigned_at=pt.assigned_at,
                    status=pt.status,
                    project_name=project.name,
                    team_name=pt.team.name if pt.team else "Неизвестная команда",
                    project_year=project.year,
                    project_semester=project.semester
                )
            )
        
        return result_list

    async def update_project_team(
        self, project_id: UUID, team_id: UUID, data: ProjectTeamUpdate
    ) -> Optional[ProjectTeamResponse]:
        """Обновить данные связи (статус)"""
        # Проверяем существование связи
        project_team = await self._project_team_repo.get_by_project_and_team(
            project_id, team_id
        )
        if not project_team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Связь между проектом и командой не найдена"
            )

        # Если меняем статус на ACTIVE, проверяем ограничения
        if data.status == ProjectTeamStatus.ACTIVE:
            project = await self._project_repo.get_by_id(project_id)
            if project:
                # Проверяем, что у команды нет других активных проектов в этом семестре
                other_active = await self._project_team_repo.get_active_project_for_team_in_semester(
                    team_id, project.year, project.semester
                )
                if other_active and other_active.project_id != project_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Команда уже участвует в активном проекте "
                              f"{other_active.project_id} в этом семестре"
                    )

        # Обновляем данные
        update_data = data.model_dump(exclude_unset=True)
        updated_obj = await self._repo.update(project_team, update_data)
        return self._to_schema(updated_obj)

    async def remove_team_from_project(
        self, project_id: UUID, team_id: UUID
    ) -> bool:
        """Удалить команду из проекта (или изменить статус)"""
        # Находим связь
        project_team = await self._project_team_repo.get_by_project_and_team(
            project_id, team_id
        )
        if not project_team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Связь между проектом и командой не найдена"
            )

        # Вместо удаления меняем статус на WITHDRAWN для истории
        project_team.status = ProjectTeamStatus.WITHDRAWN
        await self._repo.session.commit()
        await self._repo.session.refresh(project_team)
        
        return True


def project_team_service_getter(
    project_team_repo: ProjectTeamRepository = Depends(project_team_repository_getter),
    project_repo: ProjectRepository = Depends(project_repository_getter),
    team_repo: TeamRepository = Depends(team_repository_getter),
) -> ProjectTeamService:
    return ProjectTeamService(project_team_repo, project_repo, team_repo)
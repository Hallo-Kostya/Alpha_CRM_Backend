from pydantic import Field
from typing import Optional, TYPE_CHECKING
from app.domain.entities.base_entity import BaseEntity
from app.domain.enums import ProjectStatus, Semester

if TYPE_CHECKING:
    from app.domain.entities.teams.team import Team


class Project(BaseEntity):
    """Доменная модель проекта"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000, alias='desription')
    goal: Optional[str] = Field(None, max_length=1000)
    requirements: Optional[str] = Field(None, max_length=2000)
    eval_criteria: Optional[str] = Field(None, max_length=2000)
    year: int = Field(..., ge=2000, le=2100)
    semester: Semester
    status: ProjectStatus = ProjectStatus.PLANNED
    teams: list['Team'] = Field(default_factory=list)

    def add_team(self, team: 'Team') -> None:
        """Добавить команду к проекту"""
        if team not in self.teams:
            self.teams.append(team)

    def start(self) -> None:
        """Запустить проект"""
        if self.status != ProjectStatus.PLANNED:
            raise ValueError("Можно запустить только запланированный проект")
        self.status = ProjectStatus.IN_PROGRESS

    def complete(self) -> None:
        """Завершить проект"""
        if self.status != ProjectStatus.IN_PROGRESS:
            raise ValueError("Можно завершить только начатый проект")
        self.status = ProjectStatus.COMPLETED
    
    def archive(self) -> None:
        """Архивировать проект"""
        self.status = ProjectStatus.ARCHIVED
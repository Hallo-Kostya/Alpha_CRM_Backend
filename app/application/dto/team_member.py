from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TeamMemberCreate(BaseModel):
    """DTO для добавления студента в команду"""
    student_id: UUID
    role: Optional[str] = None
    study_group: Optional[str] = None


class TeamMemberUpdate(BaseModel):
    """DTO для обновления данных связи студент-команда"""
    role: Optional[str] = None
    study_group: Optional[str] = None

class TeamMemberWithTeamInfo(BaseModel):
    """DTO с информацией о связи и команде"""
    team_id: UUID
    student_id: UUID
    role: Optional[str] = None
    study_group: Optional[str] = None
    team_name: str  # Добавляем название команды
    team_group_link: Optional[str] = None  # Ссылка на чат команды
    
    model_config = ConfigDict(from_attributes=True)
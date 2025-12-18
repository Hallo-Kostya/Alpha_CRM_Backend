from datetime import datetime
from uuid import UUID
from typing import Optional, Any
from pydantic import BaseModel, field_validator, ConfigDict

from app.domain.enums.project_team_status import ProjectTeamStatus
from app.domain.enums.semester import Semester


class ProjectTeamCreate(BaseModel):
    """DTO для добавления команды к проекту"""
    team_id: UUID
    status: ProjectTeamStatus = ProjectTeamStatus.ACTIVE


class ProjectTeamUpdate(BaseModel):
    """DTO для обновления данных связи проект-команда"""
    status: Optional[ProjectTeamStatus] = None


class ProjectTeamResponse(BaseModel):
    """DTO для ответа с информацией о связи проект-команда"""
    project_id: UUID
    team_id: UUID
    assigned_at: datetime
    status: ProjectTeamStatus
    
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )
    
    @field_validator('project_id', 'team_id', mode='before')
    @classmethod
    def validate_uuid(cls, v: Any) -> UUID:
        """Валидатор для конвертации UUID"""
        if isinstance(v, UUID):
            return v
        try:
            return UUID(str(v))
        except (ValueError, TypeError, AttributeError) as e:
            raise ValueError(f"Invalid UUID value: {v}") from e


class ProjectTeamWithInfo(BaseModel):
    """DTO с расширенной информацией о связи"""
    project_id: UUID
    team_id: UUID
    assigned_at: datetime
    status: ProjectTeamStatus
    project_name: str
    team_name: str
    project_year: int
    project_semester: Semester  # Оставляем как Semester
    
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )
    
    @field_validator('project_id', 'team_id', mode='before')
    @classmethod
    def validate_uuid(cls, v: Any) -> UUID:
        if isinstance(v, UUID):
            return v
        try:
            return UUID(str(v))
        except (ValueError, TypeError, AttributeError) as e:
            raise ValueError(f"Invalid UUID value: {v}") from e
    
    @field_validator('project_semester', mode='before')
    @classmethod
    def validate_semester(cls, v: Any) -> Semester:
        """Конвертируем в Semester из строки или значения"""
        if isinstance(v, Semester):
            return v
        
        if isinstance(v, str):
            try:
                # Пробуем создать Semester из строки
                return Semester(v)
            except ValueError:
                # Если строка не совпадает с именем enum, проверяем значения
                for semester in Semester:
                    if semester.value == v:
                        return semester
                raise ValueError(f"Invalid semester string: {v}")
        
        # Если это int (например, из базы данных)
        if isinstance(v, int):
            for semester in Semester:
                if semester.value == str(v):
                    return semester
            raise ValueError(f"Invalid semester integer: {v}")
        
        raise ValueError(f"Cannot convert {type(v)} to Semester")
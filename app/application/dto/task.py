from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


class TaskCreate(BaseModel):
    """DTO для создания задачи"""
    description: str


class TaskUpdate(BaseModel):
    """DTO для обновления задачи"""
    description: Optional[str] = None
    is_completed: Optional[bool] = None


class TaskResponse(BaseModel):
    """DTO для ответа с информацией о задаче"""
    id: UUID
    description: str
    is_completed: bool
    model_config = ConfigDict(from_attributes=True)


class MeetingTaskCreate(BaseModel):
    """DTO для добавления задачи в встречу"""
    task_id: UUID
    description: Optional[str] = None  # Если не указан, создаем новую задачу


class MeetingTaskResponse(BaseModel):
    """DTO для связи встречи и задачи"""
    meeting_id: UUID
    task_id: UUID
    description: str
    is_completed: bool
    
    model_config = ConfigDict(from_attributes=True)
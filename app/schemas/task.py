"""Task schema models."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Task(BaseModel):
    """Task full model with all fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    description: str
    is_completed: bool = False


class TaskCreate(BaseModel):
    """Create task."""
    description: str


class TaskUpdate(BaseModel):
    """Update task."""
    description: Optional[str] = None
    is_completed: Optional[bool] = None


# Aliases for backward compatibility
TaskRead = Task
TaskResponse = Task


class MeetingTaskCreate(BaseModel):
    """DTO for adding a task to a meeting."""
    task_id: UUID
    description: Optional[str] = None  # If not specified, create a new task


class MeetingTaskResponse(BaseModel):
    """DTO for meeting-task relationship."""
    meeting_id: UUID
    task_id: UUID
    description: str
    is_completed: bool
    
    model_config = ConfigDict(from_attributes=True)

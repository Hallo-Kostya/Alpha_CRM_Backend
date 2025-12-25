from uuid import UUID
from pydantic import BaseModel, ConfigDict


class MeetingTask(BaseModel):
    """Доменная модель связи встречи и задачи"""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True
    )
    
    meeting_id: UUID
    task_id: UUID
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from app.domain.enums import AttendanceEntityType


class Attendance(BaseModel):
    """Посещаемость встречи"""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )
    
    meeting_id: UUID
    entity_id: UUID
    entity_type: AttendanceEntityType
    is_present: bool = False
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID


class TeamMember(BaseModel):
    """Связь между командой и студентом"""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )
    
    team_id: UUID
    student_id: UUID
    role: Optional[str] = Field(None, max_length=100)
    study_group: Optional[str] = Field(None, max_length=50)
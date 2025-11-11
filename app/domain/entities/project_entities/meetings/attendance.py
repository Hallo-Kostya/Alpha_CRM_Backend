from uuid import UUID
from app.domain.enums import AttendanceEntityType

class Attendance(): 
    def __init__(self, meeting_id: UUID, entity_id: UUID, entity_type: AttendanceEntityType, is_present: bool):
        self.meeting_id = meeting_id
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.is_present = is_present
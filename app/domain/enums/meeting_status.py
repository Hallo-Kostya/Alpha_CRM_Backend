from enum import auto
from app.domain.enums import StrAutoEnum

class MeetingStatus(StrAutoEnum):
    SCHEDULED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    CANCELED  = auto()
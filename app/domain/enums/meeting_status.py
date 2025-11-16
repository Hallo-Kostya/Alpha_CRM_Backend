from enum import auto
from .str_auto_enum import StrAutoEnum

class MeetingStatus(StrAutoEnum):
    SCHEDULED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    CANCELED  = auto()
from enum import auto
from .str_auto_enum import StrAutoEnum


class AttendanceEntityType(StrAutoEnum):
    STUDENT = auto()
    CURATOR = auto()
from enum import auto
from app.domain.enums import StrAutoEnum


class AttendanceEntityType(StrAutoEnum):
    STUDENT = auto()
    CURATOR = auto()
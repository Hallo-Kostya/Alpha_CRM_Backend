from enum import auto
from app.domain.enums import StrAutoEnum

class ProjectStatus(StrAutoEnum):
    PLANNED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    ARCHIVED = auto()
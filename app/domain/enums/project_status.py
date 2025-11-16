from enum import auto
from .str_auto_enum import StrAutoEnum

class ProjectStatus(StrAutoEnum):
    PLANNED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    ARCHIVED = auto()
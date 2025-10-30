from enum import Enum, auto

class ProjectStatus(Enum):
    PLANNED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    ARCHIVED = auto()
from enum import auto
from .str_auto_enum import StrAutoEnum

class ArtifactEntityType(StrAutoEnum):
    TEAM = auto()
    MEETING = auto()
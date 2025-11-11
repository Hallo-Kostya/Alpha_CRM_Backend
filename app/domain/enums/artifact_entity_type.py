from enum import auto
from app.domain.enums import StrAutoEnum

class ArtifactEntityType(StrAutoEnum):
    TEAM = auto()
    MEETING = auto()
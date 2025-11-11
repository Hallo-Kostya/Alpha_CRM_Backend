from enum import auto
from app.domain.enums import StrAutoEnum

class ArtifactType(StrAutoEnum):
    FILE = auto()
    VIDEO = auto()
    LINK = auto()
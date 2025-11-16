from enum import auto
from .str_auto_enum import StrAutoEnum

class ArtifactType(StrAutoEnum):
    FILE = auto()
    VIDEO = auto()
    LINK = auto()
from enum import auto
from .str_auto_enum import StrAutoEnum

class MilestoneType(StrAutoEnum):
    CONTROL_POINT = auto()
    PROTECTION = auto()
from enum import auto
from .str_auto_enum import StrAutoEnum


class EvaluationType(StrAutoEnum):
    LIKE = auto()
    DISLIKE = auto()
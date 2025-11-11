from enum import auto
from app.domain.enums.str_auto_enum import StrAutoEnum


class EvaluationType(StrAutoEnum):
    LIKE = auto()
    DISLIKE = auto()
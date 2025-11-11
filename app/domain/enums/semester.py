from enum import auto
from app.domain.enums import StrAutoEnum

class Semester(StrAutoEnum):
    AUTUMN = auto()
    SPRING = auto()
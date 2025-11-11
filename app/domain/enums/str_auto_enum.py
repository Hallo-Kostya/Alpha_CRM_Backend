from enum import Enum

class StrAutoEnum(str, Enum):
    def _generate_next_value_(name):
        return name.lower()
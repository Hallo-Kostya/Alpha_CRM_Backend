from pydantic import Field, EmailStr
from typing import Optional
from app.domain.entities.base_entity import BaseEntity


class Person(BaseEntity):
    """Базовая сущность персоны"""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    patronymic: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    tg_link: Optional[str] = Field(None, max_length=255)

    def full_name(self) -> str:
        """Получить полное имя"""
        if self.patronymic:
            return f"{self.first_name} {self.last_name} {self.patronymic}"
        return f"{self.first_name} {self.last_name}"

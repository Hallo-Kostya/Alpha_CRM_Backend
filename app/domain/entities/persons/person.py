from pydantic import Field
from typing import Optional
from app.domain.entities.base_entity import BaseEntity
from app.domain.entities.custom_types import EmailField, NameField, TgField


class Person(BaseEntity):
    """Базовая сущность персоны"""

    first_name: NameField = Field(..., examples=["Иван"])
    last_name: NameField = Field(..., examples=["Иванов"])
    patronymic: Optional[NameField] = Field(None, examples=["Иванович"])
    email: EmailField
    tg_link: TgField

    def full_name(self) -> str:
        """Получить полное имя"""
        if self.patronymic:
            return f"{self.first_name} {self.last_name} {self.patronymic}"
        return f"{self.first_name} {self.last_name}"

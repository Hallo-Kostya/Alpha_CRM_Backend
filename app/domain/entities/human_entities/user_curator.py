from typing import Optional
from uuid import UUID
from app.domain.entities import BaseEntity

class User(BaseEntity):
    def __init__(self, first_name: str, last_name: str, email: Optional[str], tg_link: Optional[str], outlook: str,
                 patronymic: Optional[str], id: Optional[UUID]):
        super().__init__(id)
        self.first_name = first_name
        self.last_name = last_name
        self.patronymic = patronymic
        self.email = email or outlook
        self.outlook = outlook
        self.tg_link = tg_link

    def full_name(self) -> str:
        if self.patronymic:
            return f"{self.first_name} {self.last_name} {self.patronymic}"
        return f"{self.first_name} {self.last_name}"
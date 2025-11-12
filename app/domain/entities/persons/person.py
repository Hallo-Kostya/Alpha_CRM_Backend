from uuid import UUID
from app.domain.entities import BaseEntity


class Person(BaseEntity):
    def __init__(self, first_name: str, last_name: str, email: str | None, tg_link: str | None, 
                 patronymic: str | None, id: UUID | None):
        super().__init__(id)
        self.first_name = first_name
        self.last_name = last_name
        self.patronymic = patronymic
        self.email = email
        self.tg_link = tg_link

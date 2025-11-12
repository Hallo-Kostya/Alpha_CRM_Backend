from typing import Optional
from uuid import UUID
from app.domain.entities import Person


class Student(Person):
    def __init__(self, first_name: str, last_name: str, email: str | None, tg_link: str | None, 
                 patronymic: str | None, id: UUID | None):
        super().__init__(first_name, last_name, email, tg_link, patronymic, id)
from typing import Optional
from uuid import UUID
from app.domain.entities import Human


class Student(Human):
    def __init__(self, first_name: str, last_name: str, email: str, tg_link: str, 
                 patronymic: Optional[str], id: Optional[UUID]):
        super().__init__(first_name, last_name, email, tg_link, patronymic, id)
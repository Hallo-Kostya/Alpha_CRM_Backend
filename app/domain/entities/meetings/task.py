from uuid import UUID
from app.domain.entities import BaseEntity


class Task(BaseEntity):
    def __init__(self, desription: str, is_completed: bool, id: UUID | None):
        super().__init__(id)
        self.desription = desription
        self.is_completed = is_completed
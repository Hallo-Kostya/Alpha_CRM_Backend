from typing import Optional
from uuid import UUID
from app.domain.entities import BaseEntity
from app.domain.entities import User

class Team(BaseEntity):
    def __init__(self, name: str, curator: User, group_link: str, id: Optional[UUID]):
        super().__init__(id)
        self.name = name
        self.curator = curator
        self.group_link = group_link
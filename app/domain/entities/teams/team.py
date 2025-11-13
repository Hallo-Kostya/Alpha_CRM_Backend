from uuid import UUID
from app.domain.entities import BaseEntity
from app.domain.entities import Curator

class Team(BaseEntity):
    def __init__(self, name: str, curator: Curator | None , group_link: str | None, id: UUID | None):
        super().__init__(id)
        self.name = name
        self.curator = curator
        self.group_link = group_link
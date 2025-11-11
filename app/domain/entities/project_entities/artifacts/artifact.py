from typing import Optional
from uuid import UUID
from app.domain.entities import BaseEntity
from app.domain.enums import ArtifactType

class Artifact(BaseEntity):
    def __init__(self, name: str, desription: str, type : ArtifactType, url: str, id: Optional[UUID]):
        super().__init__(id)
        self.name = name
        self.desription = desription
        self.type = type
        self.url = url
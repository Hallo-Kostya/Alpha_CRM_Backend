from uuid import UUID
from app.domain.entities import BaseEntity
from app.domain.enums import ArtifactEntityType


class ArtifactLink(BaseEntity):
    def __init__(self, artifact_id: UUID, entity_type: ArtifactEntityType, entity_id: UUID):
        self.artifact_id = artifact_id
        self.entity_type = entity_type
        self.entity_id = entity_id
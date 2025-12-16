from pydantic import BaseModel, ConfigDict
from uuid import UUID
from app.domain.enums import ArtifactEntityType


class ArtifactLink(BaseModel):
    """Связь артефакта с сущностью (команда, встреча)"""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )
    
    artifact_id: UUID
    entity_type: ArtifactEntityType
    entity_id: UUID
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TeamCreate(BaseModel):
    name: str
    group_link: Optional[str] = None


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    group_link: Optional[str] = None


class TeamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    group_link: Optional[str] = None

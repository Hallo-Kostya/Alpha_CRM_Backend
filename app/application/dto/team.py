from typing import Optional
from pydantic import BaseModel


class TeamCreate(BaseModel):
    name: str
    group_link: Optional[str] = None


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    group_link: Optional[str] = None
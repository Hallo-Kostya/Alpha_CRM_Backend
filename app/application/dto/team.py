# app/application/schemas/team.py

from typing import Optional

from pydantic import BaseModel
from app.domain.entities.teams.team import Team


class TeamCreate(BaseModel):
    name: str
    group_link: Optional[str] = None


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    group_link: Optional[str] = None


TeamRead = Team
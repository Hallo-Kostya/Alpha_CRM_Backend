from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    email: Optional[str] = None
    tg_link: Optional[str] = None


class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None
    email: Optional[str] = None
    tg_link: Optional[str] = None


class StudentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    email: Optional[str] = None
    tg_link: Optional[str] = None

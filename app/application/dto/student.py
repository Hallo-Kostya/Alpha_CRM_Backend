
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.custom_types import NameField


class StudentCreate(BaseModel):
    first_name: NameField = Field(..., examples=["Имя студента"])
    last_name: NameField = Field(..., examples=["Фамилия студента"])
    patronymic: Optional[NameField] = Field(None, examples=["Отчество студента"])
    email: Optional[str] = None
    tg_link: Optional[str] = None


class StudentUpdate(BaseModel):
    first_name: Optional[NameField] = Field(None, examples=["Имя студента"])
    last_name: Optional[NameField] = Field(None, examples=["Фамилия студента"])
    patronymic: Optional[NameField] = Field(None, examples=["Отчество студента"])
    email: Optional[str] = None
    tg_link: Optional[str] = None

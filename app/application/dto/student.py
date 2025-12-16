# app/application/schemas/student.py

from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from app.domain.entities.persons.student import Student


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


# Чтение — прямо доменная модель
StudentRead = Student
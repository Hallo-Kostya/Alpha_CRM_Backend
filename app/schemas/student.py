from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.common.fields import NameField


class Student(BaseModel):
    """Student model with all fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    email: Optional[str] = None
    tg_link: Optional[str] = None
    
    def full_name(self) -> str:
        """Get full name."""
        if self.patronymic:
            return f"{self.first_name} {self.last_name} {self.patronymic}"
        return f"{self.first_name} {self.last_name}"


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


class StudentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    email: Optional[str] = None
    tg_link: Optional[str] = None


class StudentSummary(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    patronymic: Optional[str] = None


class StudentDetailed(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    email: str
    tg_link: str


class StudentSummaryResponse(BaseModel):
    total: int
    students: list[StudentSummary]


class StudentDetailedResponse(BaseModel):
    total: int
    students: list[StudentDetailed]


# Aliases for backward compatibility
StudentRead = Student
StudentResponse = Student

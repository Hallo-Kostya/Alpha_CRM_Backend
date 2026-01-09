from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.domain.entities.custom_types import NameField


class CuratorPostBase(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=52)


class CuratorPOST(CuratorPostBase):
    first_name: NameField = Field(..., examples=["Имя"])
    last_name: NameField = Field(..., examples=["Фамилия"])
    patronymic: Optional[NameField] = Field(None, examples=["Отчество"])
    tg_link: Optional[str] = None


class CuratorPATCH(BaseModel):
    first_name: Optional[NameField] = Field(None, examples=["Имя"])
    last_name: Optional[NameField] = Field(None, examples=["Фамилия"])
    patronymic: Optional[NameField] = Field(None, examples=["Отчество"])
    email: Optional[EmailStr] = None
    tg_link: Optional[str] = None
    avatar_s3_path: Optional[str] = None

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class CuratorPostBase(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=52)


class CuratorPOST(CuratorPostBase):
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    tg_link: Optional[str] = None


class CuratorPATCH(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None
    email: Optional[EmailStr] = None
    tg_link: Optional[str] = None
    avatar_s3_path: Optional[str] = None

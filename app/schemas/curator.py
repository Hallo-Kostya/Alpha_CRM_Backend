"""Curator schema models."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.common.fields import NameField


class Curator(BaseModel):
    """Curator full model with all fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    email: str
    tg_link: Optional[str] = None
    avatar_s3_path: Optional[str] = None
    teams: list = Field(default_factory=list)
    
    def full_name(self) -> str:
        """Get full name."""
        if self.patronymic:
            return f"{self.first_name} {self.last_name} {self.patronymic}"
        return f"{self.first_name} {self.last_name}"


class CuratorCreate(BaseModel):
    """Create curator - used for registration."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=52)
    first_name: NameField = Field(..., examples=["Имя"])
    last_name: NameField = Field(..., examples=["Фамилия"])
    patronymic: Optional[NameField] = Field(None, examples=["Отчество"])
    tg_link: Optional[str] = None


class CuratorUpdate(BaseModel):
    """Update curator."""
    first_name: Optional[NameField] = Field(None, examples=["Имя"])
    last_name: Optional[NameField] = Field(None, examples=["Фамилия"])
    patronymic: Optional[NameField] = Field(None, examples=["Отчество"])
    email: Optional[EmailStr] = None
    tg_link: Optional[str] = None
    avatar_s3_path: Optional[str] = None


class CuratorLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


# Aliases for backward compatibility
CuratorPostBase = CuratorCreate  # Since CuratorCreate has email and password
CuratorPOST = CuratorCreate
CuratorPATCH = CuratorUpdate


# Aliases for backward compatibility
CuratorRead = Curator
CuratorResponse = Curator

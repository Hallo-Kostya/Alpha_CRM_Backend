from pydantic import Field, EmailStr
from typing import Optional
from typing_extensions import Annotated

NameField = Annotated[str, Field(..., min_length=1, max_length=64)]
EmailField = Annotated[Optional[EmailStr], Field(None, max_length=64, examples=["user@example.com"])]
TgField = Annotated[Optional[str], Field(None, max_length=64, examples=["@username"])]
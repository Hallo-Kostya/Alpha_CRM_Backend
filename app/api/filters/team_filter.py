import uuid

from pydantic import BaseModel


class TeamFilter(BaseModel):
    id: uuid.UUID | None = None
    name: str | None = None
    vk_sender_id: int | None = None

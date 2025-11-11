from typing import Optional
from uuid import uuid4, UUID

class BaseEntity:
    def __init__(self, id: Optional[UUID]):
        self.id = id or str(uuid4())
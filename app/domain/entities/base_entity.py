from uuid import uuid4, UUID

class BaseEntity:
    def __init__(self, id: UUID | None = None):
        self.id = id or str(uuid4())
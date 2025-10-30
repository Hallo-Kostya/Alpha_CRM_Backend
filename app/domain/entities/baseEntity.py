from uuid import uuid4

class BaseEntity:
    def __init__(self, id: str | None = None):
        self.id = id or str(uuid4())
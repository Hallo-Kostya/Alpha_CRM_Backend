from uuid import UUID
from app.domain.enums import EvaluationType


class Evaluation():
    def __init__(self, project_id: UUID, curator_id: UUID, type: EvaluationType, comment: str):
        self.project_id = project_id
        self.curator_id = curator_id
        self.type = type
        self.comment = comment
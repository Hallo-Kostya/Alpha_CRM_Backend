from app.domain.enums.project_status import ProjectStatus
from app.domain.enums.semester import Semester
from app.domain.entities import BaseEntity
from uuid import UUID

class Project(BaseEntity):
    def __init__(self, name: str, desription: str | None, goal : str | None, requirements: str | None, 
                 eval_criteria: str | None, year: int, semester: Semester,
                   status: ProjectStatus, id: UUID | None):
        super().__init__(id)
        self.name = name
        self.description = desription
        self.goal = goal
        self.requirements = requirements
        self.eval_criteria = eval_criteria
        self.year = year 
        self.semester = semester
        self.status = status

    def start(self):
        if self.status != ProjectStatus.PLANNED:
            raise ValueError("Можно запустить только запланированный проект")
        self.status = ProjectStatus.IN_PROGRESS

    def complete(self):
        if self.status != ProjectStatus.COMPLETED:
            raise ValueError("Можно завершить только начатый проект")
        self.status = ProjectStatus.COMPLETED
    
    def archive(self):
        self.status = ProjectStatus.ARCHIVED
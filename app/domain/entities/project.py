from app.domain.enums.projectStatus import ProjectStatus
from app.domain.enums.semester import Semester
from app.domain.entities.baseEntity import BaseEntity

class project(BaseEntity):
    def __init__(self, name: str, desription: str, goal : str, requirements: str, eval_criteria: str, year: int, semester: Semester, status: ProjectStatus, id: str | None = None):
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
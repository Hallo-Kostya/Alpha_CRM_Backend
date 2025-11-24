from app.domain.entities.projects.project import Project
from app.infrastructure.database.mappers.mapper import Mapper
from app.infrastructure.database.models.projects.project import ProjectModel


class ProjectMapper(Mapper):
    def __init__(self, team_mapper : Mapper):
        self.team_mapper = team_mapper

    def to_domain(self, model: ProjectModel) -> Project:
        return Project(
            id=model.id,
            name=model.name,
            desription=model.description,
            goal=model.goal,
            requirements=model.requirements,
            eval_criteria=model.eval_criteria,
            year=model.year,
            semester=model.semester,
            status=model.status,
            teams=[self.team_mapper.to_domain(t) for t in model.teams] 
                                    if model.project_teams else None
        )

    def to_model(self, entity: Project) -> ProjectModel:
        return ProjectModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            goal=entity.goal,
            requirements=entity.requirements,
            eval_criteria=entity.eval_criteria,
            year=entity.year,
            semester=entity.semester,
            status=entity.status,
        )
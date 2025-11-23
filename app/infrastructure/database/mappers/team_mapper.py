from app.domain.entities.teams.team import Team
from app.infrastructure.database.models.teams.team import TeamModel
from app.infrastructure.database.mappers.mapper import Mapper

class TeamMapper(Mapper):
    def __init__(self, project_mapper: Mapper, curator_mapper: Mapper) -> None:
        self.project_mapper = project_mapper
        self.curator_mapper = curator_mapper
        
    def to_domain(self, model: TeamModel) -> Team:
        return Team(
            id=model.id,
            name=model.name,
            curator=self.curator_mapper.to_domain(model.curator),
            group_link=model.group_link,
            projects=[self.project_mapper.to_domain(p) for p in model.projects] 
                                    if model.projects else []
        )

    def to_model(self, entity: Team) -> TeamModel:
        model = TeamModel(
            id=entity.id,
            name=entity.name,
            group_link=entity.group_link,
        )
        return model

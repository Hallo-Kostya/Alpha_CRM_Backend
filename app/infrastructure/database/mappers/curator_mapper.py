from app.domain.entities.persons.curator import Curator
from app.infrastructure.database.mappers.mapper import Mapper
from app.infrastructure.database.models.persons.curator import CuratorModel

class CuratorMapper(Mapper):
    def __init__(self, team_mapper: Mapper, auth_token_mapper: Mapper, oauth_token_mapper: Mapper) -> None:
        self.team_mapper = team_mapper
        self.auth_token_mapper = auth_token_mapper
        self.oauth_token_mapper = oauth_token_mapper

    def to_domain(self, model: CuratorModel) -> Curator:
        return Curator(
            id=model.id,
            first_name=model.first_name,
            last_name=model.last_name,
            patronymic=model.patronymic,
            email=model.email,
            tg_link=model.tg_link,
            outlook=model.outlook,
            password_hash=model.password_hash,
            teams=[self.team_mapper.to_domain(team) for team in model.teams]
                                    if model.teams else None,
            auth_tokens=[self.auth_token_mapper.to_domain(token) for token in model.auth_tokens]
                                    if model.auth_tokens else None,
            oauth_tokens=[self.oauth_token_mapper.to_domain(token)  for token in model.oauthtokens]
                                    if model.oauthtokens else None,
        )
    
    def to_model(self, entity: Curator) -> CuratorModel:
        return CuratorModel(
            id=entity.id,
            first_name=entity.first_name,
            last_name=entity.last_name,
            patronymic=entity.patronymic,
            email=entity.email,
            tg_link=entity.tg_link,
            outlook=entity.outlook,
            password_hash=entity.password_hash,

        )
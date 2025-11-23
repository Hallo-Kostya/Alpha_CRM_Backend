from app.domain.entities.persons.curator import Curator
from app.infrastructure.database.mappers.mapper import Mapper
from app.infrastructure.database.models.persons.curator import CuratorModel

class CuratorMapper(Mapper):
    def to_domain(self, model: CuratorModel) -> Curator:
        return Curator(
            id=model.id,
            first_name=model.first_name,
            last_name=model.last_name,
            patronymic=model.patronymic,
            email=model.email,
            tg_link=model.tg_link,
            outlook=model.outlook_email
        )
    
    def to_model(self, entity: Curator) -> CuratorModel:
        return CuratorModel(
            id=entity.id,
            first_name=entity.first_name,
            last_name=entity.last_name,
            patronymic=entity.patronymic,
            email=entity.email,
            tg_link=entity.tg_link,
            outlook=entity.outlook
        )
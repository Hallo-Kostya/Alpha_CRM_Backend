from uuid import UUID
from app.domain.entities import Person

class Curator(Person):
    def __init__(self, first_name: str, last_name: str, email: str | None , tg_link: str | None, outlook: str,
                 patronymic: str | None , id: UUID | None):
        super().__init__(first_name, last_name, email, tg_link, patronymic, id)
        self.outlook = outlook
        self.tg_link = tg_link

    def full_name(self) -> str:
        if self.patronymic:
            return f"{self.first_name} {self.last_name} {self.patronymic}"
        return f"{self.first_name} {self.last_name}"
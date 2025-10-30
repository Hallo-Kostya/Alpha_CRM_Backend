from baseEntity import BaseEntity

class User(BaseEntity):
    def __init__(self, first_name: str, last_name: str, email: str,  
                 tg_link: str, 
                 patronymic: str | None = None, id: str | None = None):
        super().__init__(id)
        self.first_name = first_name
        self.last_name = last_name
        self.patronymic = patronymic
        self.email = email
        self.tg_link = tg_link

    def full_name(self) -> str:
        if self.patronymic:
            return f"{self.first_name} {self.last_name} {self.patronymic}"
        return f"{self.first_name} {self.last_name}"
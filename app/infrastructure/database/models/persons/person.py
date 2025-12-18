from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.entity_base import BaseEntity

class PersonModel(BaseEntity):
    """Базовая модель для всех персон (Person, Student, Curator)"""
    __tablename__ = "persons"
    __abstract__ = True
    # Имя
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Фамилия
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Отчество
    patronymic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Email
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Ссылка на Telegram
    tg_link: Mapped[str | None] = mapped_column(String(255), nullable=True)


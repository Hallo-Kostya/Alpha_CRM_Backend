from sqlalchemy.orm import DeclarativeBase
from app.infrastructure.database.base import Base

class BaseAssociation(DeclarativeBase):
    """Базовый класс для association таблиц без автоматического id"""
    __abstract__ = True
    metadata = Base.metadata


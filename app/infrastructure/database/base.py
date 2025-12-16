from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from app.core.config import settings

class Base(DeclarativeBase):
    """Общий базовый класс для всех моделей — один registry на всё приложение"""
    metadata = MetaData(naming_convention=settings.db.naming_convention)
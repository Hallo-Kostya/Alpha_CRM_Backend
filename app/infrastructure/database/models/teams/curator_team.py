from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.infrastructure.database.base_association import BaseAssociation

if TYPE_CHECKING:
    from app.infrastructure.database.models.persons.curator import CuratorModel
    from app.infrastructure.database.models.teams.team import TeamModel


class CuratorTeamModel(BaseAssociation):
    """Модель связи куратора и команды (many-to-many)"""
    __tablename__ = "curator_teams"

    # FK на куратора (curator)
    curator_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("curators.id", ondelete="CASCADE"),
        primary_key=True,
    )
    # FK на команду (team)
    team_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        primary_key=True,
    )

    __table_args__ = (
        UniqueConstraint("curator_id", "team_id", name="uq_curator_teams_curator_team"),
    )

    # Отношение к куратору
    curator: Mapped["CuratorModel"] = relationship(
        "CuratorModel",
        back_populates="curator_team_links",
    )
    # Отношение к команде
    team: Mapped["TeamModel"] = relationship(
        "TeamModel",
        back_populates="curator_team_links",
    )

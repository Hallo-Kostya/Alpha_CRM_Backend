from typing import Optional, Any, Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.infrastructure.database.repositories.base_repository import (
    BaseRepository,
)
from app.infrastructure.database.models import (
    ProjectApplicationModel,
    ProjectModel,
    ProjectInterviewModel,
)
from app.infrastructure.database.database import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


FILTERS_MAP = {
    "id": ProjectApplicationModel.id,
    "project_id": ProjectApplicationModel.project_id,
    "vk_sender_id": ProjectApplicationModel.vk_sender_id,
    "status": ProjectApplicationModel.status,
    "mean_project_score": ProjectApplicationModel.mean_project_score,
    "project_name": ProjectModel.name,
    "year": ProjectModel.year,
    "semester": ProjectModel.semester,
    "interview_status": ProjectInterviewModel.interview_status,
}


class ProjectApplicationRepository(BaseRepository[ProjectApplicationModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(ProjectApplicationModel, session)

    async def get_list(
        self,
        filters: Optional[dict[str, Any]] = None,
        range_filters: Optional[dict[str, tuple[Any, Any]]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        eager_loads: list[str] | None = None,
    ) -> tuple[int, Sequence[ProjectApplicationModel]]:
        query = select(self.model).join(
            ProjectModel, ProjectModel.id == self.model.project_id
        )

        # Filtering
        if filters:
            conditions = []

            for key, value in filters.items():
                column = FILTERS_MAP.get(key)

                if column is None or value is None:
                    continue

                if isinstance(value, Sequence) and not isinstance(value, str):
                    conditions.append(column.in_(value))
                else:
                    conditions.append(column == value)
            if conditions:
                query = query.where(*conditions)

        if eager_loads:
            options = []

            for load_path in eager_loads:
                parts = load_path.split(".")

                attr = getattr(self.model, parts[0])
                loader = selectinload(attr)

                current_model = attr.property.entity.class_

                for part in parts[1:]:
                    attr = getattr(current_model, part)
                    loader = loader.selectinload(attr)
                    current_model = attr.property.entity.class_

                options.append(loader)

            query = query.options(*options)

        if range_filters:
            for field, (from_val, to_val) in range_filters.items():
                column = getattr(self.model, field, None)
                if column is not None:
                    if from_val is not None:
                        query = query.where(column >= from_val)
                    if to_val is not None:
                        query = query.where(column <= to_val)

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query)

        if order_by:
            desc = order_by.startswith("-")
            column = getattr(self.model, order_by.lstrip("-"), None)
            if column is not None:
                query = query.order_by(column.desc() if desc else column.asc())
        else:
            query = query.order_by(self.model.created_at.asc())

        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return total, result.scalars().unique().all()


def project_applications_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> BaseRepository:
    repository = ProjectApplicationRepository(session)
    return repository

import pytest
from uuid import uuid4
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.infrastructure.database.models.projects.project import ProjectModel
from app.application.services.projects_service import ProjectService
from app.application.dto.project import ProjectCreateMinimal, ProjectUpdate
from app.domain.entities.projects.project import Project
from app.domain.enums.semester import Semester
from app.domain.enums.project_status import ProjectStatus


def make_service(session: AsyncSession) -> ProjectService:
    repo = BaseRepository(ProjectModel, session)
    return ProjectService(repo)


def test_compute_status_logic():
    svc = ProjectService(None)  # repo not used for compute_status

    now = datetime.now()
    current_year = now.year
    current_sem = Semester.SPRING if now.month < 7 else Semester.AUTUMN

    # future year -> PLANNED
    assert svc.compute_status(current_year + 1, current_sem) == ProjectStatus.PLANNED
    # past year -> COMPLETED
    assert svc.compute_status(current_year - 1, current_sem) == ProjectStatus.COMPLETED
    # same year, same semester -> IN_PROGRESS
    assert svc.compute_status(current_year, current_sem) == ProjectStatus.IN_PROGRESS
    # same year, other semester -> COMPLETED
    other_sem = Semester.AUTUMN if current_sem is Semester.SPRING else Semester.SPRING
    assert svc.compute_status(current_year, other_sem) == ProjectStatus.COMPLETED


@pytest.mark.asyncio
async def test_create_minimal_sets_status(session: AsyncSession):
    service = make_service(session)

    now = datetime.now()
    current_year = now.year
    current_sem = Semester.SPRING if now.month < 7 else Semester.AUTUMN

    # create with only name – defaults should be applied
    proj0 = ProjectCreateMinimal(name="JustName")
    created0: Project = await service.create(proj0)
    assert created0.year == current_year
    assert created0.semester == current_sem
    assert created0.status == ProjectStatus.IN_PROGRESS

    # simulate missing values (e.g. request sets `null` or data got stripped)
    proj_null = ProjectCreateMinimal(name="Nulls", year=None, semester=None)
    created_null: Project = await service.create(proj_null)
    assert created_null.year == current_year
    assert created_null.semester == current_sem
    assert created_null.status == ProjectStatus.IN_PROGRESS

    # create but force custom status (should be respected)
    proj_force = ProjectCreateMinimal(
        name="Manual", year=current_year, semester=current_sem, status=ProjectStatus.PLANNED
    )
    created_force = await service.create(proj_force)
    assert created_force.status == ProjectStatus.PLANNED

    # create future project explicitly
    proj = ProjectCreateMinimal(name="Future", year=current_year + 1, semester=current_sem)
    created: Project = await service.create(proj)
    assert created.status == ProjectStatus.PLANNED

    # create current project with same semester
    proj2 = ProjectCreateMinimal(name="Now", year=current_year, semester=current_sem)
    created2: Project = await service.create(proj2)
    assert created2.status == ProjectStatus.IN_PROGRESS

    # create current project with other semester
    # proj3 = ProjectCreateMinimal(name="PastSem", year=current_year, semester=other_sem)
    # created3: Project = await service.create(proj3)
    # assert created3.status == ProjectStatus.COMPLETED


@pytest.mark.asyncio
async def test_update_status_based_on_date(session: AsyncSession):
    service = make_service(session)

    now = datetime.now()
    current_year = now.year
    current_sem = Semester.SPRING if now.month < 7 else Semester.AUTUMN
    other_sem = Semester.AUTUMN if current_sem is Semester.SPRING else Semester.SPRING

    # start with a past project and ensure it can move to IN_PROGRESS
    proj_in_past = ProjectCreateMinimal(
        name="Transition", year=current_year, semester=current_sem, status=ProjectStatus.COMPLETED
    )
    created = await service.create(proj_in_past)
    assert created.status == ProjectStatus.IN_PROGRESS or created.status == ProjectStatus.COMPLETED
    # manually update to PLANNED for test
    await service.update(created.id, ProjectUpdate(status=ProjectStatus.PLANNED))
    result = await service.update_status_based_on_date(created.id)
    assert result.status == service.compute_status(current_year, current_sem)

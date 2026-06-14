from uuid import UUID
from fastapi import APIRouter, Depends, Query
from app.api.dependencies import get_current_curator
from app.api.filters.project_application_filter import ProjectInterviewFilter
from app.services.project_application_service import (
    ProjectApplicationService,
    project_application_service_getter,
)
from app.services.projects_service import ProjectService, project_service_getter
from app.schemas.project import ProjectRead
from app.schemas.project_application import (
    ProjectApplicationGET,
    ProjectApplicationPATCH,
    ProjectApplicationGETLimited,
    ProjectApplicationPOST,
    ProjectInterviewGET,
    ProjectInterviewGETLimited,
    ProjectInterviewPATCH,
    ProjectInterviewPOST,
)
from app.infrastructure.database.database import db_helper
from app.api.filters import ProjectApplicationFilter, ProjectFilter
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.common.enums import (
    ProjectApplicationStatus,
    ProjectInterviewStatus,
    ProjectStatus,
)
from app.common.utils import get_curr_year_and_semester


router = APIRouter(
    prefix="/project_applications",
    tags=["project_applications"],
    dependencies=[Depends(get_current_curator)],
)


@router.get(
    "/{vk_sender_id}/available_projects",
    response_model=list[ProjectRead],
    summary="Получить доступные проекты для юзера вк",
)
async def get_available_projects(
    vk_sender_id: int,
    project_service: ProjectService = Depends(project_service_getter),
    application_service: ProjectApplicationService = Depends(
        project_application_service_getter
    ),
) -> list[ProjectRead]:
    sent_applications = await application_service.get_applications(
        ProjectApplicationFilter(vk_sender_id=vk_sender_id), eager_loads=["members"]
    )
    applied_projects_ids = [application.project_id for application in sent_applications]  # type: ignore[union-attr]
    curr_year, curr_semester = get_curr_year_and_semester()
    proj_filter = ProjectFilter(
        status=ProjectStatus.PLANNED, semester=curr_semester, year=curr_year
    )
    return await project_service.get_projects_with_excluded_ids(
        applied_projects_ids, proj_filter.model_dump(exclude_unset=True)
    )


@router.post(
    "/", response_model=ProjectApplicationGETLimited, summary="Создать заявку на проект"
)
async def post_project_application(
    data: ProjectApplicationPOST,
    application_service: ProjectApplicationService = Depends(
        project_application_service_getter
    ),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> ProjectApplicationGETLimited:
    created_obj = await application_service.create_application(data, session)
    return created_obj


@router.get(
    "/",
    response_model=list[ProjectApplicationGET],
    summary="Получить все заявки на проекты",
)
async def get_project_applications(
    application_filters: ProjectApplicationFilter = Depends(),
    application_service: ProjectApplicationService = Depends(
        project_application_service_getter
    ),
) -> list[ProjectApplicationGET]:
    applications = await application_service.get_applications(
        application_filters,
        True,
        ["project", "members", "interview", "interview.artifacts"],
    )
    return applications  # type: ignore[return-value]


@router.patch(
    "/{application_id}/",
    response_model=ProjectApplicationGETLimited,
    summary="Частично обновить заявку",
)
async def edit_project_application(
    application_id: UUID,
    data: ProjectApplicationPATCH,
    application_service: ProjectApplicationService = Depends(
        project_application_service_getter
    ),
) -> ProjectApplicationGETLimited:
    application = await application_service.update_project_application(
        application_id, data
    )
    return application


@router.delete(
    "/{application_id}/",
    summary="Удалить заявку",
)
async def delete_project_application(
    application_id: UUID,
    application_service: ProjectApplicationService = Depends(
        project_application_service_getter
    ),
) -> dict:
    await application_service.delete_application(application_id)
    return {"success": f"Successfully deleted application with id {application_id}"}


@router.patch(
    "/{application_id}/change_status/",
    summary="Изменить статус заявки",
)
async def change_status_project_application(
    application_id: UUID,
    new_status: ProjectApplicationStatus,
    application_service: ProjectApplicationService = Depends(
        project_application_service_getter
    ),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> ProjectApplicationGETLimited:
    updated_schema = await application_service.handle_status_change(
        application_id, new_status, session
    )
    return updated_schema


@router.post(
    "/{application_id}/interview/",
    summary="Создать интервью",
)
async def create_interview(
    application_id: UUID,
    interview_data: ProjectInterviewPOST,
    application_service: ProjectApplicationService = Depends(
        project_application_service_getter
    ),
) -> ProjectInterviewGETLimited:
    updated_schema = await application_service.create_interview(
        application_id, interview_data.interview_date
    )
    return updated_schema


@router.get(
    "/interviews/",
    summary="Получить список интервью",
)
async def get_interviews(
    interview_filters: ProjectInterviewFilter = Depends(),
    interview_status: list[ProjectInterviewStatus] | None = Query(None),
    application_service: ProjectApplicationService = Depends(
        project_application_service_getter
    ),
) -> list[ProjectApplicationGET]:
    interview_filters.interview_status = interview_status
    applications = await application_service.get_applications(
        interview_filters,
        True,
        ["project", "members", "interview", "interview.artifacts"],
    )
    return applications  # type: ignore[return-value]


@router.patch("/interviews/{interview_id}/")
async def update_interview(
    interview_id: UUID,
    data: ProjectInterviewPATCH,
    application_service: ProjectApplicationService = Depends(
        project_application_service_getter
    ),
) -> ProjectInterviewGET:
    updated_interview = await application_service.update_interview(interview_id, data)
    return updated_interview

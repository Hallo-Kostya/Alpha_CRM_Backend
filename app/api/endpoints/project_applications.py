from fastapi import APIRouter, Depends
from app.services.project_application_service import (
    ProjectApplicationService,
    project_application_service_getter,
)
from app.services.projects_service import ProjectService, project_service_getter
from app.schemas.project import ProjectRead
from app.schemas.project_application import (
    ProjectApplicationGET,
    ProjectApplicationPATCH,
    ProjectApplicationPOST,
)
from app.api.filters import ProjectApplicationFilter, ProjectFilter
from app.common.enums import ProjectStatus, Semester
from app.services.team_service import TeamService, team_service_getter
from app.common.utils import get_curr_year_and_semester


router = APIRouter(
    prefix="/project_applications",
    tags=["project_applications"],
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
    sent_applications = await application_service.get_applications(ProjectApplicationFilter(vk_sender_id=vk_sender_id), ["team", "project", "meeting", "team.members"])
    applied_projects_ids = [application.project.id for application in sent_applications]
    curr_year, curr_semester = get_curr_year_and_semester()
    proj_filter = ProjectFilter(status=ProjectStatus.PLANNED, semester=curr_semester, year=curr_year)
    return await project_service.get_projects_with_excluded_ids(applied_projects_ids, proj_filter.model_dump(exclude_unset=True))
    

@router.post("/", response_model=ProjectApplicationGET, summary="Создать заявку на проект")
async def post_project_application(data: ProjectApplicationPOST, application_service: ProjectApplicationService = Depends(
        project_application_service_getter
    )) -> ProjectApplicationGET:
    created_obj = await application_service.create_application(data)
    return created_obj


@router.get("/", response_model=list[ProjectApplicationGET], summary="Получить все заявки на проекты")
async def get_project_applications(filters: ProjectApplicationFilter = Depends(), application_service: ProjectApplicationService = Depends(
        project_application_service_getter
    )) -> list[ProjectApplicationGET]:
    applications = await application_service.get_applications(filters, ["team", "project", "team.members"])
    return applications
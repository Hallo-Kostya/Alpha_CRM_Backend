from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from uuid import UUID
from itertools import chain
from fastapi import Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio.session import AsyncSession
from typing import Callable, Iterable, Sequence
from app.common.utils import (
    get_curr_year_and_semester,
    split_fullname,
    get_next_week_range,
)
from app.infrastructure.database.models.meetings.meeting import BaseMeetingModel
from app.infrastructure.database.models.projects.project_application import (
    ProjectInterviewModel,
)
from app.schemas.project_application import (
    ProjectApplicationGET,
    ProjectApplicationPATCH,
    ProjectApplicationPOST,
    ProjectInterviewGET,
    TeamMemberPOST,
    ProjectApplicationGETLimited,
)
from app.infrastructure.database.models import (
    ProjectModel,
    TeamModel,
    ProjectApplicationModel,
    TeamMemberModel,
    ProjectTeamModel,
    StudentModel,
    ProjectApplicationMemberModel,
)
from app.sdk.vk_bot_backend_sdk import VkBotBackendSdk, get_sdk
from app.infrastructure.database.repositories.project_repository import (
    ProjectRepository,
    project_repository_getter,
)
from app.infrastructure.database.repositories.team_repository import (
    TeamRepository,
    team_repository_getter,
)
from app.infrastructure.database.repositories.project_team_repository import (
    ProjectTeamRepository,
    project_team_repository_getter,
)
from app.infrastructure.database.repositories.student_repository import (
    StudentRepository,
    student_repository_getter,
)
from app.infrastructure.database.repositories.team_member_repository import (
    TeamMemberRepository,
    team_member_repository_getter,
)
from app.infrastructure.database.repositories.meeting_repository import (
    MeetingRepository,
    meeting_repository_getter,
)
from app.infrastructure.database.repositories.project_applications import (
    ProjectApplicationRepository,
    ProjectApplicationMemberRepository,
    ProjectInterviewRepository,
    project_application_members_repository_getter,
    project_interview_repository_getter,
    project_applications_repository_getter,
)
from app.api.filters import ProjectApplicationFilter
from app.common.enums import (
    ProjectApplicationStatus,
    ProjectInterviewStatus,
    ProjectStatus,
)
from app.core.config import settings


class ProjectApplicationService:
    """Application service for project applications"""

    def __init__(
        self,
        project_application_repo: ProjectApplicationRepository,
        application_member_repo: ProjectApplicationMemberRepository,
        interview_repo: ProjectInterviewRepository,
        project_team_repo: ProjectTeamRepository,
        project_repo: ProjectRepository,
        team_repo: TeamRepository,
        student_repo: StudentRepository,
        tm_repo: TeamMemberRepository,
        meeting_repo: MeetingRepository,
        vk_bot_sdk: VkBotBackendSdk,
    ):
        self._project_application_repo = project_application_repo
        self._application_member_repo = application_member_repo
        self._interview_repo = interview_repo
        self._project_team_repo = project_team_repo
        self._project_repo = project_repo
        self._team_repo = team_repo
        self._tm_repo = tm_repo
        self._student_repo = student_repo
        self._meeting_repo = meeting_repo
        self._vk_bot_sdk = vk_bot_sdk
        self._status_change_handlers: dict[ProjectApplicationStatus, Callable] = {
            ProjectApplicationStatus.INTERVIEW: self._handle_interview_status,
            ProjectApplicationStatus.DECLINED: self._handle_declined_status,
            ProjectApplicationStatus.ACCEPTED: self._handle_accepted_status,
        }

    def _to_orm(self, scheme: ProjectApplicationPOST) -> ProjectApplicationModel:
        """Convert schema to ORM model."""
        return ProjectApplicationModel(**scheme.model_dump(exclude_unset=True))

    def _to_schema(self, orm_model: ProjectApplicationModel) -> ProjectApplicationGET:
        """Convert ORM model to schema."""
        return ProjectApplicationGET.model_validate(orm_model, from_attributes=True)

    def _to_limited_schema(
        self, orm_model: ProjectApplicationModel
    ) -> ProjectApplicationGETLimited:
        return ProjectApplicationGETLimited.model_validate(
            orm_model, from_attributes=True
        )

    async def _get_project(self, project_id: UUID) -> ProjectModel:
        """Check project existence."""
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} is not found",
            )
        return project

    async def _get_applications_by_vk_id(
        self, vk_sender_id: int
    ) -> Sequence[ProjectApplicationModel]:
        """Check project and team existence."""
        _, applications_objs = await self._project_application_repo.get_list(
            {"vk_sender_id": vk_sender_id}
        )
        return applications_objs

    async def _validate_project(self, project: ProjectModel) -> None:
        curr_year, curr_semester = get_curr_year_and_semester()
        if any(
            (
                project.status != ProjectStatus.PLANNED,
                project.year != curr_year,
                project.semester != curr_semester,
            )
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project with id {project.id} is not available for apply at this time",
            )

    async def _validate_vk_sender(self, vk_sender_id: int, project_id: UUID) -> None:
        _, applications_objs = await self._project_application_repo.get_list(
            {"vk_sender_id": vk_sender_id, "project_id": project_id}
        )
        if applications_objs:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User already has been aplied for this project {project_id}, user: {vk_sender_id}",
            )

    async def _get_team_prev_projects_mean_rate(self, team_name: str) -> float:
        team = await self._get_team(team_name)
        if not team:
            return 0.0
        _, prev_projs = await self._project_team_repo.get_list({"team_id": team.id})
        prev_projs_rates = [proj["final_score"] for proj in prev_projs]
        mean_score = 0.0
        if prev_projs_rates:
            mean_score = sum(prev_projs_rates) / len(prev_projs_rates)
        return mean_score

    async def _validate_data(self, data: ProjectApplicationPOST) -> None:
        await self._validate_vk_sender(data.vk_sender_id, data.project_id)
        project = await self._get_project(data.project_id)
        await self._validate_project(project)

    async def _get_team(
        self,
        team_name: str | None = None,
        team_id: UUID | None = None,
    ) -> TeamModel | None:
        if not any((team_name, team_id)):
            return None
        filters: dict[str, str | UUID] = {}
        if team_id:
            filters["id"] = team_id
        if team_name:
            filters["name"] = team_name
        _, teams = await self._team_repo.get_list(filters)
        return next(iter(teams), None)

    async def _get_student_by_fullname(self, fullname: str) -> StudentModel | None:
        last_name, first_name, patronymic = split_fullname(fullname)
        if not (first_name or last_name):
            raise ValueError(f"Got wrong student fullname: {fullname}")
        filters = {
            "last_name": last_name,
            "first_name": first_name,
            "patronymic": patronymic,
        }
        _, result = await self._student_repo.get_list(filters)
        return next(iter(result), None)

    def _map_project_app_members(
        self,
        team_members: list[TeamMemberPOST],
    ) -> list[ProjectApplicationMemberModel]:
        result = []
        for team_member in team_members:
            obj = ProjectApplicationMemberModel(
                fullname=team_member.fullname,
                role=team_member.role,
                study_group=team_member.study_group,
            )
            result.append(obj)
        return result

    async def create_application(
        self, data: ProjectApplicationPOST, session: AsyncSession
    ) -> ProjectApplicationGETLimited:
        """Create team's project application"""
        try:
            await self._validate_data(data)
            project_app_members = self._map_project_app_members(data.team_members)
            data.mean_project_score = await self._get_team_prev_projects_mean_rate(
                data.team_name
            )
            application_dto = ProjectApplicationModel(
                project_id=data.project_id,
                description=data.description,
                team_name=data.team_name,
                vk_sender_id=data.vk_sender_id,
                status=data.status,
                mean_project_score=data.mean_project_score,
                members=project_app_members,
            )
            session.add(application_dto)
            await session.commit()
            return self._to_limited_schema(application_dto)
        except Exception:
            await session.rollback()
            raise

    async def update_project_application(
        self,
        application_id: UUID,
        new_data: ProjectApplicationPATCH,
    ) -> ProjectApplicationGETLimited:
        """Update project application."""
        app_obj = await self._project_application_repo.get_by_id(
            application_id, ["members"]
        )
        if not app_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID {application_id} is not found",
            )
        existing_members = {m.id: m for m in app_obj.members}
        if new_data.team_members:
            new_members = []
            for member in new_data.team_members:
                member_obj = existing_members.get(member.id)
                if not member_obj:
                    member_obj = ProjectApplicationMemberModel(
                        **member.model_dump(exclude_unset=True)
                    )
                    member_obj.project_application_id = app_obj.id
                else:
                    member_data_to_update = member.model_dump(exclude_unset=True)
                    for key, value in member_data_to_update.items():
                        setattr(member_obj, key, value)
                new_members.append(member_obj)
            app_obj.members = new_members
        data_to_update = new_data.model_dump(
            exclude_unset=True, exclude={"team_members"}
        )
        new_obj = await self._project_application_repo.update(app_obj, data_to_update)
        return self._to_limited_schema(new_obj)

    async def delete_application(self, application_id: UUID) -> Response:
        project_app = await self._project_application_repo.get_by_id(application_id)
        if not project_app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID {application_id} is not found",
            )
        await self._project_application_repo.delete(project_app)
        return Response(
            f"Successfuly deleted application with id: {application_id}",
            status_code=200,
        )

    async def get_applications(
        self,
        filters: ProjectApplicationFilter,
        detailed: bool = False,
        eager_loads: list[str] | None = None,
    ) -> list[ProjectApplicationGETLimited | ProjectApplicationGET]:
        _, applications = await self._project_application_repo.get_list(
            filters=filters.model_dump(exclude_none=True), eager_loads=eager_loads
        )
        if detailed:
            return [self._to_schema(application) for application in applications]
        return [self._to_limited_schema(application) for application in applications]

    async def handle_status_change(
        self,
        application_id: UUID,
        new_status: ProjectApplicationStatus,
        session: AsyncSession,
    ):
        app_obj = await self._project_application_repo.get_by_id(
            application_id, eager_loads=["project", "interview", "members"]
        )
        if not app_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID {application_id} is not found",
            )
        handler_func = self._status_change_handlers.get(new_status)
        if handler_func:
            new_obj = await handler_func(app_obj, session)
            return self._to_limited_schema(new_obj)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown project application status: {new_status}",
        )

    async def _handle_declined_status(
        self,
        application_obj: ProjectApplicationModel,
        session: AsyncSession,
    ) -> ProjectApplicationModel:
        if application_obj.status == ProjectApplicationStatus.DECLINED:
            return application_obj
        try:
            application_obj.status = ProjectApplicationStatus.DECLINED
            _, linked_interview = await self._interview_repo.get_list(
                {"project_application_id": application_obj.id}
            )
            if linked_interview:
                linked_interview = linked_interview[0]
                if linked_interview.interview_status not in (
                    ProjectInterviewStatus.RATED,
                    ProjectInterviewStatus.CANCELED,
                ):
                    linked_interview.interview_status = ProjectInterviewStatus.CANCELED
                    session.add(linked_interview)
            session.add(application_obj)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        await self._vk_bot_sdk.post_declined_application(
            application_obj.vk_sender_id,
            application_obj.project.name,
            application_obj.team_name,
        )
        return application_obj

    async def _get_all_calls(
        self, start_date: datetime, end_date: datetime
    ) -> Iterable[BaseMeetingModel]:
        _, items = await self._meeting_repo.get_list(
            range_filters={"date": (start_date, end_date)},
            order_by="date",
        )
        _, items_interviews = await self._interview_repo.get_list(
            range_filters={"date": (start_date, end_date)},
            order_by="date",
        )
        return chain(items, items_interviews)

    def _calculate_possible_slots(
        self,
        all_meetings: Iterable[BaseMeetingModel],
        min_workday: datetime,
        max_workday: datetime,
    ) -> list[str]:
        possible_slots = []
        busy_slots = set()
        for meeting in all_meetings:
            meeting_date = meeting.date.astimezone(ZoneInfo("Asia/Yekaterinburg"))
            if meeting_date.minute >= 30:
                slot = meeting_date.replace(minute=0, second=0, microsecond=0)
                busy_slots.add(slot)
                busy_slots.add(slot + timedelta(hours=1))
            else:
                slot = meeting_date.replace(minute=0, second=0, microsecond=0)
                busy_slots.add(slot)
        min_range_hour = settings.curator_workday_start_hour
        max_range_hour = settings.curator_workday_end_hour
        current_day = min_workday.astimezone(ZoneInfo("Asia/Yekaterinburg"))
        max_workday = max_workday.astimezone(ZoneInfo("Asia/Yekaterinburg"))
        while current_day.date() <= max_workday.date():
            if current_day.weekday() == 5 or current_day.weekday() == 6:
                current_day += timedelta(days=1)
                continue
            for hour in range(min_range_hour, max_range_hour):
                current_slot = current_day.replace(hour=hour)
                if current_slot not in busy_slots:
                    possible_slots.append(current_slot.isoformat())
            current_day += timedelta(days=1)
        return possible_slots

    async def _handle_interview_status(
        self,
        application_obj: ProjectApplicationModel,
        session: AsyncSession,
    ) -> ProjectApplicationModel:
        if application_obj.status == ProjectApplicationStatus.INTERVIEW:
            return application_obj
        try:
            start_date, end_date = get_next_week_range()
            all_calls = await self._get_all_calls(start_date, end_date)
            possible_dates = self._calculate_possible_slots(
                all_calls, start_date, end_date
            )
            application_obj.status = ProjectApplicationStatus.INTERVIEW
            session.add(application_obj)
        except Exception:
            await session.rollback()
            raise
        await session.commit()
        await self._vk_bot_sdk.post_interview_possible_dates(
            application_obj.vk_sender_id,
            possible_dates,
            application_obj.project.name,
            application_obj.team_name,
            application_obj.id,
        )
        return application_obj

    async def _handle_accepted_status(
        self,
        application_obj: ProjectApplicationModel,
        session: AsyncSession,
    ) -> ProjectApplicationModel:
        if application_obj.status == ProjectApplicationStatus.ACCEPTED:
            return application_obj
        try:
            application_obj.status = ProjectApplicationStatus.ACCEPTED
            _, linked_interview = await self._interview_repo.get_list(
                {"project_application_id": application_obj.id}
            )
            session.add(application_obj)
            if linked_interview:
                linked_interview = linked_interview[0]
                if linked_interview.interview_status == ProjectInterviewStatus.WAITING:
                    linked_interview.interview_status = ProjectInterviewStatus.CANCELED
                elif linked_interview.interview_status == ProjectInterviewStatus.RATING:
                    linked_interview.interview_status = ProjectInterviewStatus.RATED
                session.add(linked_interview)
            await self._create_team_project_from_application(application_obj, session)
            await session.commit()
            await self._team_repo.session.commit()
        except Exception:
            await session.rollback()
            await self._team_repo.session.rollback()
            raise
        await self._vk_bot_sdk.post_accepted_application(
            application_obj.vk_sender_id,
            application_obj.project.name,
            application_obj.team_name,
        )
        return application_obj

    async def _create_team_project_from_application(
        self, application_obj: ProjectApplicationModel, session: AsyncSession
    ) -> None:
        team_obj = TeamModel(
            name=application_obj.team_name,
        )
        self._team_repo.session.add(team_obj)
        await session.flush()
        await session.refresh(team_obj)
        team_members = []
        for member in application_obj.members:
            student_model = await self._get_student_by_fullname(member.fullname)
            if not student_model:
                last_name, first_name, patronymic = split_fullname(member.fullname)
                new_student = StudentModel(
                    last_name=last_name,
                    first_name=first_name,
                    patronymic=patronymic,
                )
                student_model = await self._student_repo.create(new_student)
            member_obj = TeamMemberModel(
                team_id=team_obj.id,
                student_id=student_model.id,
                role=member.role,
                study_group=member.study_group,
            )
            team_members.append(member_obj)
            session.add(member_obj)
        team_obj.members = team_members
        session.add(team_obj)
        project_team_model = ProjectTeamModel(
            project_id=application_obj.project_id, team_id=team_obj.id
        )
        session.add(project_team_model)

    async def create_interview(
        self, application_id: UUID, interview_date: datetime
    ) -> ProjectInterviewGET:
        app_obj = await self._project_application_repo.get_by_id(
            application_id, eager_loads=["project", "interview", "members"]
        )
        if not app_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID {application_id} is not found",
            )
        if not app_obj.interview:
            new_obj = ProjectInterviewModel(
                project_application_id=app_obj.id,
                date=interview_date,
                name=f"Собеседование команды: {app_obj.team_name} на проект: {app_obj.project.name}",
            )
            created_obj = await self._interview_repo.create(new_obj)
        else:
            created_obj = await self._interview_repo.update(
                app_obj.interview,
                {
                    "date": interview_date,
                    "name": f"Собеседование команды: {app_obj.team_name} на проект: {app_obj.project.name}",
                    "interview_status": ProjectInterviewStatus.NEW,
                },
            )
        return ProjectInterviewGET.model_validate(created_obj, from_attributes=True)


def project_application_service_getter(
    project_team_repo: ProjectTeamRepository = Depends(project_team_repository_getter),
    app_members_repo: ProjectApplicationMemberRepository = Depends(
        project_application_members_repository_getter
    ),
    interviews_repo: ProjectInterviewRepository = Depends(
        project_interview_repository_getter
    ),
    team_repo: TeamRepository = Depends(team_repository_getter),
    project_repo: ProjectRepository = Depends(project_repository_getter),
    project_application_repo: ProjectApplicationRepository = Depends(
        project_applications_repository_getter
    ),
    student_repo: StudentRepository = Depends(student_repository_getter),
    tm_repo: TeamMemberRepository = Depends(team_member_repository_getter),
    meeting_repo: MeetingRepository = Depends(meeting_repository_getter),
    vk_bot_sdk: VkBotBackendSdk = Depends(get_sdk),
) -> ProjectApplicationService:
    return ProjectApplicationService(
        project_application_repo,
        app_members_repo,
        interviews_repo,
        project_team_repo,
        project_repo,
        team_repo,
        student_repo,
        tm_repo,
        meeting_repo,
        vk_bot_sdk,
    )

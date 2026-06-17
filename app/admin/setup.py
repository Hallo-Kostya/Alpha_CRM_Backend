from sqladmin import ModelView

from app.infrastructure.database.models import (
    CuratorModel,
    StudentModel,
    TeamModel,
    ProjectModel,
    MeetingModel,
    TaskModel,
    ProjectApplicationModel,
    ProjectApplicationMemberModel,
    ProjectInterviewModel,
)
from app.infrastructure.database.models.artifacts.artifact import ArtifactModel
from app.infrastructure.database.models.artifacts.artifact_link import ArtifactLinkModel


class CuratorAdmin(ModelView, model=CuratorModel):
    column_list = [
        CuratorModel.id,
        CuratorModel.email,
        CuratorModel.first_name,
        CuratorModel.last_name,
    ]

    column_searchable_list = [
        CuratorModel.email,
        CuratorModel.first_name,
        CuratorModel.last_name,
    ]

    column_sortable_list = [CuratorModel.created_at]

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    form_columns = [
        "email",
        "first_name",
        "last_name",
        "patronymic",
        "tg_link",
        "hashed_password",
    ]


class StudentAdmin(ModelView, model=StudentModel):
    column_list = [
        StudentModel.id,
        StudentModel.first_name,
        StudentModel.last_name,
        StudentModel.email,
    ]

    column_searchable_list = [
        StudentModel.first_name,
        StudentModel.last_name,
        StudentModel.email,
    ]


class TeamAdmin(ModelView, model=TeamModel):
    column_list = [TeamModel.id, TeamModel.name]

    column_details_list = [
        TeamModel.name,
        TeamModel.group_link,
    ]


class ProjectAdmin(ModelView, model=ProjectModel):
    column_list = [
        ProjectModel.id,
        ProjectModel.name,
        ProjectModel.year,
        ProjectModel.semester,
    ]


class MeetingAdmin(ModelView, model=MeetingModel):
    column_list = [
        MeetingModel.id,
        MeetingModel.name,
        MeetingModel.date,
        MeetingModel.status,
    ]


class TaskAdmin(ModelView, model=TaskModel):
    column_list = [
        TaskModel.id,
        TaskModel.description,
        TaskModel.is_completed,
    ]


class ArtifactAdmin(ModelView, model=ArtifactModel):
    name = "Artifact"
    name_plural = "Artifacts"

    column_list = [
        ArtifactModel.id,
        ArtifactModel.name,
        ArtifactModel.type,
        ArtifactModel.size,
        ArtifactModel.content_type,
        ArtifactModel.created_at,
    ]

    column_searchable_list = [
        ArtifactModel.name,
        ArtifactModel.content_type,
        ArtifactModel.checksum,
    ]

    column_sortable_list = [
        ArtifactModel.created_at,
        ArtifactModel.size,
    ]

    can_create = False
    can_edit = False

    can_view_details = True

    form_excluded_columns = [
        "artifact_links",
    ]


class ArtifactLinkAdmin(ModelView, model=ArtifactLinkModel):
    name = "Artifact Link"
    name_plural = "Artifact Links"

    column_list = [
        ArtifactLinkModel.id,
        ArtifactLinkModel.artifact_id,
        ArtifactLinkModel.entity_type,
        ArtifactLinkModel.entity_id,
    ]

    column_searchable_list = [
        ArtifactLinkModel.entity_type,
    ]

    can_create = False
    can_edit = False

    can_view_details = True


class ProjectApplicationAdmin(ModelView, model=ProjectApplicationModel):
    name = "Project Application"
    name_plural = "Project Applications"

    column_list = [
        ProjectApplicationModel.id,
        ProjectApplicationModel.team_name,
        ProjectApplicationModel.project_id,
        ProjectApplicationModel.status,
    ]

    column_searchable_list = [
        ProjectApplicationModel.team_name,
    ]

    can_create = False
    can_edit = False

    can_view_details = True


class ProjectInterviewAdmin(ModelView, model=ProjectInterviewModel):
    name = "Project Interview"
    name_plural = "Project Interviews"

    column_list = [
        ProjectInterviewModel.id,
        ProjectInterviewModel.interview_status,
        ProjectInterviewModel.date,
        ProjectInterviewModel.project_application_id,
    ]

    column_searchable_list = [
        ProjectInterviewModel.id,
        ProjectInterviewModel.date,
    ]

    can_create = False
    can_edit = False

    can_view_details = True


class ProjectApplicationMemberAdmin(ModelView, model=ProjectApplicationMemberModel):
    name = "Project Application Member"
    name_plural = "Project Application Members"

    column_list = [
        ProjectApplicationMemberModel.id,
        ProjectApplicationMemberModel.fullname,
        ProjectApplicationMemberModel.role,
        ProjectApplicationMemberModel.study_group,
    ]

    column_searchable_list = [
        ProjectInterviewModel.id,
        ProjectApplicationMemberModel.fullname,
    ]

    can_create = False
    can_edit = False

    can_view_details = True

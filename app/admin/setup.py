from sqladmin import Admin, ModelView
from sqlalchemy.orm import selectinload, joinedload
from app.infrastructure.database.models import (
    CuratorModel,
    StudentModel,
    TeamModel,
    ProjectModel,
    MeetingModel,
    TaskModel,
    TeamMemberModel,
    ProjectApplicationModel,
)
from app.core.database import db_helper


class RulesMixin:
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class CuratorAdmin(ModelView, RulesMixin, model=CuratorModel):
    # Колонки в списке
    column_list = [
        CuratorModel.id,
        CuratorModel.email,
        CuratorModel.first_name,
        CuratorModel.last_name,
    ]

    # Поиск по полям
    column_searchable_list = [
        CuratorModel.email,
        CuratorModel.first_name,
        CuratorModel.last_name,
    ]

    # Сортировка
    column_sortable_list = [CuratorModel.created_at]

    # Поля в форме создания/редактирования
    form_columns = [
        "email",
        "first_name",
        "last_name",
        "patronymic",
        "tg_link",
        "hashed_password",
    ]


class StudentAdmin(ModelView, RulesMixin, model=StudentModel):
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


class TeamAdmin(ModelView, RulesMixin, model=TeamModel):
    column_list = [
        TeamModel.id,
        TeamModel.name,
    ]


class ProjectAdmin(ModelView, RulesMixin, model=ProjectModel):
    column_list = [
        ProjectModel.id,
        ProjectModel.name,
        ProjectModel.year,
        ProjectModel.semester,
    ]


class MeetingAdmin(ModelView, RulesMixin, model=MeetingModel):
    column_list = [
        MeetingModel.id,
        MeetingModel.name,
        MeetingModel.date,
        MeetingModel.status,
    ]


class TaskAdmin(ModelView, RulesMixin, model=TaskModel):
    column_list = [TaskModel.id, TaskModel.description, TaskModel.is_completed]


class TeamMemberAdmin(ModelView, RulesMixin, model=TeamMemberModel):
    column_list = [
        TeamMemberModel.id,
        TeamMemberModel.team,
        TeamMemberModel.student,
        TeamMemberModel.role,
    ]


class ProjectApplicationAdmin(ModelView, RulesMixin, model=ProjectApplicationModel):
    column_list = [
        ProjectApplicationModel.id,
        ProjectApplicationModel.team,
        ProjectApplicationModel.project,
        ProjectApplicationModel.vk_sender_id,
        ProjectApplicationModel.status,
        ProjectApplicationModel.meeting,
        ProjectApplicationModel.mean_project_score,
    ]

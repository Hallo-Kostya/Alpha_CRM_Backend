# Импорт всех моделей для Alembic и удобного доступа
from app.infrastructure.database.models.persons import (
    PersonModel,
    StudentModel,
    CuratorModel,
)
from app.infrastructure.database.models.teams import (
    TeamModel,
    TeamMemberModel,
    CuratorTeamModel,
)
from app.infrastructure.database.models.projects import (
    ProjectModel,
    MilestoneModel,
    EvaluationModel,
    ProjectTeamModel,
)
from app.infrastructure.database.models.meetings import (
    MeetingModel,
    TaskModel,
    AttendanceModel,
    MeetingTaskModel,
)
from app.infrastructure.database.models.artifacts import (
    ArtifactModel,
    ArtifactLinkModel,
)

__all__ = [
    # Persons
    "PersonModel",
    "StudentModel",
    "CuratorModel",
    # Teams
    "TeamModel",
    "TeamMemberModel",
    "CuratorTeamModel",
    # Projects
    "ProjectModel",
    "MilestoneModel",
    "EvaluationModel",
    "ProjectTeamModel",
    # Meetings
    "MeetingModel",
    "TaskModel",
    "AttendanceModel",
    "MeetingTaskModel",
    # Artifacts
    "ArtifactModel",
    "ArtifactLinkModel",
]


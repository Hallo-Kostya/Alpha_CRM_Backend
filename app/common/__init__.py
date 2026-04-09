"""Common module with shared enums and field types."""
from .enums import (
    StrAutoEnum,
    Semester,
    ProjectStatus,
    ProjectTeamStatus,
    MeetingStatus,
    ArtifactType,
    EvaluationType,
    ArtifactEntityType,
    AttendanceEntityType,
    MilestoneType,
)
from .fields import (
    NameField,
    EmailField,
    TgField,
    ShortText,
    LongText,
    MediumText,
)

__all__ = [
    # Enums
    "StrAutoEnum",
    "Semester",
    "ProjectStatus",
    "ProjectTeamStatus",
    "MeetingStatus",
    "ArtifactType",
    "EvaluationType",
    "ArtifactEntityType",
    "AttendanceEntityType",
    "MilestoneType",
    # Fields
    "NameField",
    "EmailField",
    "TgField",
    "ShortText",
    "LongText",
    "MediumText",
]

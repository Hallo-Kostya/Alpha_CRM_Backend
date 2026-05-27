"""Common enums for all schemas and models."""

from enum import Enum, auto


class StrAutoEnum(str, Enum):
    """Base enum that automatically generates string values from names."""

    def _generate_next_value_(name, start, count, last_values):
        return name.upper()


class Semester(StrAutoEnum):
    """Academic semester."""

    AUTUMN = auto()
    SPRING = auto()


class ProjectStatus(StrAutoEnum):
    """Project status."""

    PLANNED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    ARCHIVED = auto()


class ProjectTeamStatus(str, Enum):
    """Status of team participation in project."""

    ACTIVE = "ACTIVE"  # Actively participating
    COMPLETED = "COMPLETED"  # Participation completed (project finished)
    WITHDRAWN = "WITHDRAWN"  # Team withdrawn from project
    PENDING = "PENDING"  # Pending confirmation


class ProjectApplicationStatus(str, Enum):
    """Status of team participation in project."""

    INTERVIEW = "INTERVIEW"  # заявка на стадии интервью
    WAITING_FOR_ACK = (
        "WAITING_FOR_ACK"  # после выставления оценки за интервью, ждет итог. решения
    )
    UNSEEN = "UNSEEN"  # новая заявка
    ACCEPTED = "ACCEPTED"  # заявка принята
    DECLINED = "DECLINED"  # заявка отклонена


class ProjectInterviewStatus(str, Enum):
    """Status of team participation in project."""

    WAITING = "WAITING"  # Новое интервью (ДО интервью)
    RATING = "RATING"  # Ждёт оценки (ПОСЛЕ интервью)
    RATED = "RATED"  # Оценка выставлена (финальный статус интервью)
    CANCELED = "CANCELED"  # Интервью отменено


class MeetingStatus(StrAutoEnum):
    """Meeting status."""

    SCHEDULED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    CANCELED = auto()


class ArtifactType(StrAutoEnum):
    """Type of artifact."""

    FILE = auto()
    VIDEO = auto()
    LINK = auto()


class EvaluationType(StrAutoEnum):
    """Type of evaluation."""

    LIKE = auto()
    DISLIKE = auto()


class ArtifactEntityType(StrAutoEnum):
    """Entity type that can have artifacts."""

    TEAM = auto()
    MEETING = auto()
    PROJECT = auto()
    INTERVIEW = auto()


class AttendanceEntityType(StrAutoEnum):
    """Entity type for attendance tracking."""

    STUDENT = auto()
    CURATOR = auto()


class MilestoneType(StrAutoEnum):
    """Type of project milestone."""

    CONTROL_POINT = auto()
    PROTECTION = auto()

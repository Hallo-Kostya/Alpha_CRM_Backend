"""Pytest configuration and shared fixtures."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4
from datetime import datetime, timezone

from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from app.main import main_app
from app.common.enums import (
    MeetingStatus, ProjectStatus, Semester, ProjectTeamStatus
)


# =============================================================================
# UUID Fixtures
# =============================================================================
@pytest.fixture
def any_uuid() -> UUID:
    return uuid4()


# Константа для фиксированного UUID (не фикстура!)
FIXED_UUID = UUID("12345678-1234-5678-1234-567812345678")


# =============================================================================
# Mock Service Fixtures
# =============================================================================
# @pytest.fixture
# def mock_auth_service():
#     """Mocked AuthService."""
#     service = AsyncMock()
#     service.create_token_pair.return_value = (
#         MagicMock(token="access_token_123", expires_at=datetime.now(timezone.utc)),
#         MagicMock(token="refresh_token_456", expires_at=datetime.now(timezone.utc)),
#     )
#     service.verify_password.return_value = True
#     service.get_hashed_pass.return_value = "hashed_password"
#     service.get_curator_id_from_access.return_value = FIXED_UUID
#     service.get_curator_id_from_refresh.return_value = FIXED_UUID
#     service.get_hash_for_string.return_value = "hashed_token"
#     service.revoke_token_pair.return_value = None
#     return service


@pytest.fixture
def mock_curator_service():
    """Mocked CuratorService."""
    service = AsyncMock()
    return service


@pytest.fixture
def mock_student_service():
    """Mocked StudentService."""
    service = AsyncMock()
    return service


@pytest.fixture
def mock_team_service():
    """Mocked TeamService."""
    service = AsyncMock()
    return service


@pytest.fixture
def mock_team_member_service():
    """Mocked TeamMemberService."""
    service = AsyncMock()
    return service


@pytest.fixture
def mock_project_service():
    """Mocked ProjectService."""
    service = AsyncMock()
    service.compute_status.return_value = ProjectStatus.IN_PROGRESS
    return service


@pytest.fixture
def mock_project_team_service():
    """Mocked ProjectTeamService."""
    service = AsyncMock()
    return service


@pytest.fixture
def mock_meeting_service():
    """Mocked MeetingService."""
    service = AsyncMock()
    return service


@pytest.fixture
def mock_task_service():
    """Mocked TaskService."""
    service = AsyncMock()
    return service


@pytest.fixture
def mock_search_service():
    """Mocked SearchService."""
    service = AsyncMock()
    return service


# =============================================================================
# HTTP Client Fixture
# =============================================================================
@pytest.fixture
async def async_client(
    mock_auth_service,
    mock_curator_service,
    mock_student_service,
    mock_team_service,
    mock_team_member_service,
    mock_project_service,
    mock_project_team_service,
    mock_meeting_service,
    mock_task_service,
    mock_search_service,
) -> AsyncClient:
    """Async HTTP client with mocked dependencies."""

    # Override dependencies
    from app.services.auth_service import auth_service_getter
    from app.services.curator_service import curator_service_getter
    from app.services.students_service import student_service_getter
    from app.services.team_service import team_service_getter
    from app.services.team_member_service import team_member_service_getter
    from app.services.projects_service import project_service_getter
    from app.services.project_team_service import project_team_service_getter
    from app.services.meeting_service import meeting_service_getter
    from app.services.task_service import task_service_getter
    from app.services.search_service import search_service_getter

    main_app.dependency_overrides[auth_service_getter] = lambda: mock_auth_service
    main_app.dependency_overrides[curator_service_getter] = lambda: mock_curator_service
    main_app.dependency_overrides[student_service_getter] = lambda: mock_student_service
    main_app.dependency_overrides[team_service_getter] = lambda: mock_team_service
    main_app.dependency_overrides[team_member_service_getter] = lambda: mock_team_member_service
    main_app.dependency_overrides[project_service_getter] = lambda: mock_project_service
    main_app.dependency_overrides[project_team_service_getter] = lambda: mock_project_team_service
    main_app.dependency_overrides[meeting_service_getter] = lambda: mock_meeting_service
    main_app.dependency_overrides[task_service_getter] = lambda: mock_task_service
    main_app.dependency_overrides[search_service_getter] = lambda: mock_search_service

    transport = ASGITransport(app=main_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    main_app.dependency_overrides.clear()


# =============================================================================
# Data Factory Fixtures
# =============================================================================
@pytest.fixture
def curator_data(any_uuid):
    return {
        "id": str(any_uuid),
        "first_name": "Иван",
        "last_name": "Иванов",
        "patronymic": "Иванович",
        "email": "ivan@example.com",
        "tg_link": "https://t.me/ivan",
        "avatar_s3_path": None,
        "teams": [],
    }


@pytest.fixture
def student_data(any_uuid):
    return {
        "id": str(any_uuid),
        "first_name": "Петр",
        "last_name": "Петров",
        "patronymic": "Петрович",
        "email": "petr@example.com",
        "tg_link": "https://t.me/petr",
    }


@pytest.fixture
def team_data(any_uuid):
    return {
        "id": str(any_uuid),
        "name": "DreamTeam",
        "group_link": "https://t.me/dreamteam",
    }


@pytest.fixture
def project_data(any_uuid):
    return {
        "id": str(any_uuid),
        "name": "AI Project",
        "description": "Cool AI project",
        "goal": "Build AI",
        "requirements": "Python, ML",
        "eval_criteria": "Accuracy > 90%",
        "year": 2026,
        "semester": "SPRING",
        "status": "IN_PROGRESS",
    }


@pytest.fixture
def meeting_data(any_uuid):
    return {
        "id": str(any_uuid),
        "name": "Sprint Planning",
        "resume": "Plan the sprint",
        "date": "2026-05-10T10:00:00+00:00",
        "status": "SCHEDULED",
        "team_id": str(any_uuid),
        "previous_meeting_id": None,
        "next_meeting_id": None,
    }


@pytest.fixture
def task_data(any_uuid):
    return {
        "id": str(any_uuid),
        "description": "Implement feature X",
        "is_completed": False,
    }
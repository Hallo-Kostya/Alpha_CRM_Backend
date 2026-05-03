"""Tests for student endpoints."""
import pytest
from uuid import UUID
from unittest.mock import MagicMock


class TestStudentCreate:
    """POST /students/"""

    @pytest.fixture
    def create_payload(self):
        return {
            "first_name": "Петр",
            "last_name": "Петров",
            "patronymic": "Петрович",
            "email": "petr@example.com",
            "tg_link": "https://t.me/petr",
        }

    async def test_create_success(self, async_client, mock_student_service, create_payload, any_uuid):
        """Create student successfully."""
        mock_student_service.create.return_value = MagicMock(
            id=any_uuid,
            **create_payload,
        )

        response = await async_client.post("/students/", json=create_payload)

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Петр"
        assert data["email"] == "petr@example.com"

    async def test_create_validation_error(self, async_client, mock_student_service):
        """Invalid data returns 422."""
        response = await async_client.post("/students/", json={"first_name": "A"})  # Too short

        assert response.status_code == 422


class TestStudentGet:
    """GET /students/{id}"""

    async def test_get_by_id_success(self, async_client, mock_student_service, student_data, any_uuid):
        """Get existing student."""
        mock_student_service.get_by_id.return_value = MagicMock(**student_data)

        response = await async_client.get(f"/students/{any_uuid}")

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Петр"

    async def test_get_by_id_not_found(self, async_client, mock_student_service, any_uuid):
        """Get non-existent student returns 404."""
        mock_student_service.get_by_id.return_value = None

        response = await async_client.get(f"/students/{any_uuid}")

        assert response.status_code == 404
        assert "не найден" in response.json()["detail"]


class TestStudentUpdate:
    """PATCH /students/{id}"""

    async def test_update_success(self, async_client, mock_student_service, student_data, any_uuid):
        """Update student successfully."""
        updated = {**student_data, "tg_link": "https://t.me/petr_new"}
        mock_student_service.update.return_value = MagicMock(**updated)

        response = await async_client.patch(
            f"/students/{any_uuid}",
            json={"tg_link": "https://t.me/petr_new"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["tg_link"] == "https://t.me/petr_new"

    async def test_update_not_found(self, async_client, mock_student_service, any_uuid):
        """Update non-existent student returns 404."""
        mock_student_service.update.return_value = None

        response = await async_client.patch(
            f"/students/{any_uuid}",
            json={"tg_link": "https://t.me/new"}
        )

        assert response.status_code == 404


class TestStudentDelete:
    """DELETE /students/{id}"""

    async def test_delete_success(self, async_client, mock_student_service, any_uuid):
        """Delete student successfully."""
        mock_student_service.delete.return_value = True

        response = await async_client.delete(f"/students/{any_uuid}")

        assert response.status_code == 204

    async def test_delete_not_found(self, async_client, mock_student_service, any_uuid):
        """Delete non-existent student returns 404."""
        mock_student_service.delete.return_value = False

        response = await async_client.delete(f"/students/{any_uuid}")

        assert response.status_code == 404


class TestStudentList:
    """GET /students/"""

    async def test_list_students(self, async_client, mock_student_service, student_data):
        """List students with summary."""
        mock_student_service.get_students_summary.return_value = MagicMock(
            total=2,
            students=[
                MagicMock(
                    id=student_data["id"],
                    first_name=student_data["first_name"],
                    last_name=student_data["last_name"],
                    patronymic=student_data["patronymic"],
                    email="petr@example.com",
                    tg_link="https://t.me/petr",
                    role=None,
                    study_group=None,
                ),
                MagicMock(
                    id="22222222-2222-2222-2222-222222222222",
                    first_name="Анна",
                    last_name="Аннова",
                    patronymic=None,
                    email="anna@example.com",
                    tg_link=None,
                    role="Team Lead",
                    study_group="ИУ10-11",
                ),
            ]
        )

        response = await async_client.get("/students/")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["students"]) == 2

    async def test_list_students_filtered_by_team(self, async_client, mock_student_service, any_uuid):
        """List students filtered by team."""
        mock_student_service.get_students_summary.return_value = MagicMock(
            total=1,
            students=[MagicMock()]
        )

        response = await async_client.get(f"/students/?team_id={any_uuid}")

        assert response.status_code == 200
        mock_student_service.get_students_summary.assert_awaited_with(
            team_id=any_uuid,
            project_id=None,
        )

    async def test_list_students_filtered_by_project(self, async_client, mock_student_service, any_uuid):
        """List students filtered by project."""
        mock_student_service.get_students_summary.return_value = MagicMock(
            total=0,
            students=[]
        )

        response = await async_client.get(f"/students/?project_id={any_uuid}")

        assert response.status_code == 200
        mock_student_service.get_students_summary.assert_awaited_with(
            team_id=None,
            project_id=any_uuid,
        )
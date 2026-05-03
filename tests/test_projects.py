"""Tests for project and project_team endpoints."""
import pytest
from uuid import UUID, uuid4
from unittest.mock import MagicMock
from datetime import datetime


class TestProjectCreate:
    """POST /projects/"""

    @pytest.fixture
    def create_payload(self):
        return {
            "name": "AI Project",
            "description": "Cool AI project",
        }

    async def test_create_minimal_success(self, async_client, mock_project_service, create_payload, any_uuid):
        """Create project with minimal fields."""
        mock_project_service.create.return_value = MagicMock(
            id=any_uuid,
            name="AI Project",
            description="Cool AI project",
            goal=None,
            requirements=None,
            eval_criteria=None,
            year=2026,
            semester="SPRING",
            status="IN_PROGRESS",
        )

        response = await async_client.post("/projects/", json=create_payload)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "AI Project"
        assert data["year"] == 2026
        assert data["status"] == "IN_PROGRESS"

    async def test_create_with_explicit_year_semester(self, async_client, mock_project_service, any_uuid):
        """Create project with explicit year and semester."""
        mock_project_service.create.return_value = MagicMock(
            id=any_uuid,
            name="Old Project",
            year=2025,
            semester="AUTUMN",
            status="COMPLETED",
        )

        payload = {
            "name": "Old Project",
            "year": 2025,
            "semester": "AUTUMN",
        }
        response = await async_client.post("/projects/", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["year"] == 2025


class TestProjectGet:
    """GET /projects/{id}"""

    async def test_get_by_id_success(self, async_client, mock_project_service, project_data, any_uuid):
        """Get existing project."""
        mock_project_service.get_by_id.return_value = MagicMock(**project_data)

        response = await async_client.get(f"/projects/{any_uuid}")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "AI Project"
        assert data["status"] == "IN_PROGRESS"

    async def test_get_by_id_not_found(self, async_client, mock_project_service, any_uuid):
        """Get non-existent project returns 404."""
        mock_project_service.get_by_id.return_value = None

        response = await async_client.get(f"/projects/{any_uuid}")

        assert response.status_code == 404


class TestProjectUpdate:
    """PATCH /projects/{id}"""

    async def test_update_success(self, async_client, mock_project_service, project_data, any_uuid):
        """Update project successfully."""
        updated = {**project_data, "description": "Updated description"}
        mock_project_service.update.return_value = MagicMock(**updated)

        response = await async_client.patch(
            f"/projects/{any_uuid}",
            json={"description": "Updated description"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"

    async def test_update_not_found(self, async_client, mock_project_service, any_uuid):
        """Update non-existent project returns 404."""
        mock_project_service.update.return_value = None

        response = await async_client.patch(
            f"/projects/{any_uuid}",
            json={"description": "New"}
        )

        assert response.status_code == 404


class TestProjectDelete:
    """DELETE /projects/{id}"""

    async def test_delete_success(self, async_client, mock_project_service, any_uuid):
        """Delete project successfully."""
        mock_project_service.delete.return_value = True

        response = await async_client.delete(f"/projects/{any_uuid}")

        assert response.status_code == 200
        assert "successfully deleted" in response.text

    async def test_delete_not_found(self, async_client, mock_project_service, any_uuid):
        """Delete non-existent project returns 404."""
        mock_project_service.delete.return_value = False

        response = await async_client.delete(f"/projects/{any_uuid}")

        assert response.status_code == 404


class TestProjectList:
    """GET /projects/"""

    async def test_list_projects_summary(self, async_client, mock_project_service, any_uuid):
        """List projects with summary."""
        mock_project_service.get_projects_summary.return_value = MagicMock(
            total=2,
            projects=[
                MagicMock(
                    id=any_uuid,
                    name="AI Project",
                    description="Cool AI",
                    teams_count=3,
                    members_count=12,
                ),
                MagicMock(
                    id=uuid4(),
                    name="Web Project",
                    description="Web app",
                    teams_count=2,
                    members_count=8,
                ),
            ]
        )

        response = await async_client.get("/projects/")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["projects"]) == 2

    async def test_list_filtered_by_year(self, async_client, mock_project_service):
        """List projects filtered by year."""
        mock_project_service.get_projects_summary.return_value = MagicMock(
            total=1,
            projects=[MagicMock()]
        )

        response = await async_client.get("/projects/?year=2026")

        assert response.status_code == 200
        mock_project_service.get_projects_summary.assert_awaited_with(
            year=2026,
            semester=None,
            team_id=None,
        )

    async def test_list_filtered_by_semester(self, async_client, mock_project_service):
        """List projects filtered by semester."""
        mock_project_service.get_projects_summary.return_value = MagicMock(
            total=0,
            projects=[]
        )

        response = await async_client.get("/projects/?semester=SPRING")

        assert response.status_code == 200
        mock_project_service.get_projects_summary.assert_awaited_with(
            year=None,
            semester="SPRING",
            team_id=None,
        )


# =============================================================================
# Project Teams
# =============================================================================
class TestProjectTeamAssign:
    """POST /projects/{project_id}/teams"""

    @pytest.fixture
    def assign_payload(self, any_uuid):
        return {
            "team_id": str(any_uuid),
            "status": "ACTIVE",
        }

    async def test_assign_team_success(self, async_client, mock_project_team_service, mock_project_service, assign_payload, any_uuid):
        """Assign team to project successfully."""
        mock_project_service.get_by_id.return_value = MagicMock(id=any_uuid)
        mock_project_team_service.assign_team_to_project.return_value = MagicMock(
            project_id=any_uuid,
            team_id=assign_payload["team_id"],
            assigned_at=datetime.now(),
            status="ACTIVE",
        )

        response = await async_client.post(
            f"/projects/{any_uuid}/teams",
            json=assign_payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ACTIVE"

    async def test_assign_team_project_not_found(self, async_client, mock_project_service, assign_payload, any_uuid):
        """Assign to non-existent project returns 404."""
        mock_project_service.get_by_id.return_value = None

        response = await async_client.post(
            f"/projects/{any_uuid}/teams",
            json=assign_payload
        )

        assert response.status_code == 404

    async def test_assign_team_already_assigned(self, async_client, mock_project_team_service, mock_project_service, assign_payload, any_uuid):
        """Assign already assigned team returns 400."""
        from fastapi import HTTPException
        mock_project_service.get_by_id.return_value = MagicMock(id=any_uuid)
        mock_project_team_service.assign_team_to_project.side_effect = HTTPException(
            status_code=400,
            detail="Team already assigned to this project"
        )

        response = await async_client.post(
            f"/projects/{any_uuid}/teams",
            json=assign_payload
        )

        assert response.status_code == 400


class TestProjectTeamRemove:
    """DELETE /projects/{project_id}/teams/{team_id}"""

    async def test_remove_team_success(self, async_client, mock_project_team_service, any_uuid):
        """Remove team from project."""
        mock_project_team_service.delete_team_from_project.return_value = True

        response = await async_client.delete(f"/projects/{any_uuid}/teams/{any_uuid}")

        assert response.status_code == 204

    async def test_remove_team_not_found(self, async_client, mock_project_team_service, any_uuid):
        """Remove non-existent link returns 404."""
        mock_project_team_service.delete_team_from_project.return_value = False

        response = await async_client.delete(f"/projects/{any_uuid}/teams/{any_uuid}")

        assert response.status_code == 404
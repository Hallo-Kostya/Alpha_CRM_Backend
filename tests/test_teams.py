"""Tests for team and team_member endpoints."""
import pytest
from uuid import UUID
from unittest.mock import MagicMock


class TestTeamCreate:
    """POST /teams/"""

    @pytest.fixture
    def create_payload(self):
        return {
            "name": "DreamTeam",
            "group_link": "https://t.me/dreamteam",
        }

    async def test_create_success(self, async_client, mock_team_service, create_payload, any_uuid):
        """Create team successfully."""
        mock_team_service.create.return_value = MagicMock(
            id=any_uuid,
            **create_payload,
        )

        response = await async_client.post("/teams/", json=create_payload)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "DreamTeam"
        assert data["group_link"] == "https://t.me/dreamteam"

    async def test_create_validation_error(self, async_client):
        """Invalid name returns 422."""
        response = await async_client.post("/teams/", json={"name": "A"})  # Too short

        assert response.status_code == 422


class TestTeamGet:
    """GET /teams/{id}"""

    async def test_get_by_id_success(self, async_client, mock_team_service, team_data, any_uuid):
        """Get existing team."""
        mock_team_service.get_by_id.return_value = MagicMock(**team_data)

        response = await async_client.get(f"/teams/{any_uuid}")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "DreamTeam"

    async def test_get_by_id_not_found(self, async_client, mock_team_service, any_uuid):
        """Get non-existent team returns 404."""
        mock_team_service.get_by_id.return_value = None

        response = await async_client.get(f"/teams/{any_uuid}")

        assert response.status_code == 404
        assert "не найдена" in response.json()["detail"]


class TestTeamUpdate:
    """PATCH /teams/{id}"""

    async def test_update_success(self, async_client, mock_team_service, team_data, any_uuid):
        """Update team successfully."""
        updated = {**team_data, "name": "SuperTeam"}
        mock_team_service.update.return_value = MagicMock(**updated)

        response = await async_client.patch(
            f"/teams/{any_uuid}",
            json={"name": "SuperTeam"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "SuperTeam"

    async def test_update_not_found(self, async_client, mock_team_service, any_uuid):
        """Update non-existent team returns 404."""
        mock_team_service.update.return_value = None

        response = await async_client.patch(
            f"/teams/{any_uuid}",
            json={"name": "SuperTeam"}
        )

        assert response.status_code == 404


class TestTeamDelete:
    """DELETE /teams/{id}"""

    async def test_delete_success(self, async_client, mock_team_service, any_uuid):
        """Delete team successfully."""
        mock_team_service.delete.return_value = True

        response = await async_client.delete(f"/teams/{any_uuid}")

        assert response.status_code == 204

    async def test_delete_not_found(self, async_client, mock_team_service, any_uuid):
        """Delete non-existent team returns 404."""
        mock_team_service.delete.return_value = False

        response = await async_client.delete(f"/teams/{any_uuid}")

        assert response.status_code == 404


class TestTeamList:
    """GET /teams/"""

    async def test_list_teams(self, async_client, mock_team_service, any_uuid):
        """List teams with summary."""
        mock_team_service.get_teams_summary.return_value = MagicMock(
            total=2,
            teams=[
                MagicMock(
                    id=any_uuid,
                    name="DreamTeam",
                    members_count=3,
                    members=[
                        MagicMock(id=uuid4(), full_name="Иван Иванов"),
                        MagicMock(id=uuid4(), full_name="Петр Петров"),
                    ],
                ),
                MagicMock(
                    id=uuid4(),
                    name="SuperTeam",
                    members_count=1,
                    members=[MagicMock(id=uuid4(), full_name="Анна Аннова")],
                ),
            ]
        )

        response = await async_client.get("/teams/")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["teams"]) == 2
        assert data["teams"][0]["members_count"] == 3

    async def test_list_teams_filtered_by_project(self, async_client, mock_team_service, any_uuid):
        """List teams filtered by project."""
        mock_team_service.get_teams_summary.return_value = MagicMock(
            total=1,
            teams=[MagicMock()]
        )

        response = await async_client.get(f"/teams/?project_id={any_uuid}")

        assert response.status_code == 200
        mock_team_service.get_teams_summary.assert_awaited_with(project_id=any_uuid)


# =============================================================================
# Team Members
# =============================================================================
class TestTeamMemberAdd:
    """POST /teams/{team_id}/students"""

    @pytest.fixture
    def member_payload(self, any_uuid):
        return {
            "student_id": str(any_uuid),
            "role": "Developer",
            "study_group": "ИУ10-11",
        }

    async def test_add_student_success(self, async_client, mock_team_member_service, member_payload, any_uuid):
        """Add student to team successfully."""
        mock_team_member_service.add_student_to_team.return_value = MagicMock(
            team_id=any_uuid,
            student_id=member_payload["student_id"],
            role="Developer",
            study_group="ИУ10-11",
        )

        response = await async_client.post(
            f"/teams/{any_uuid}/students",
            json=member_payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "Developer"
        assert data["study_group"] == "ИУ10-11"

    async def test_add_student_already_in_team(self, async_client, mock_team_member_service, member_payload, any_uuid):
        """Add student already in team returns 400."""
        from fastapi import HTTPException
        mock_team_member_service.add_student_to_team.side_effect = HTTPException(
            status_code=400,
            detail="Студент уже состоит в этой команде"
        )

        response = await async_client.post(
            f"/teams/{any_uuid}/students",
            json=member_payload
        )

        assert response.status_code == 400


class TestTeamMemberUpdate:
    """PATCH /teams/{team_id}/students/{student_id}"""

    async def test_update_member_success(self, async_client, mock_team_member_service, any_uuid):
        """Update student role and group."""
        mock_team_member_service.update_student_role_and_group.return_value = MagicMock(
            team_id=any_uuid,
            student_id=str(any_uuid),
            role="Team Lead",
            study_group="ИУ10-12",
        )

        response = await async_client.patch(
            f"/teams/{any_uuid}/students/{any_uuid}",
            json={"role": "Team Lead", "study_group": "ИУ10-12"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "Team Lead"

    async def test_update_member_not_found(self, async_client, mock_team_member_service, any_uuid):
        """Update non-existent member returns 404."""
        from fastapi import HTTPException
        mock_team_member_service.update_student_role_and_group.side_effect = HTTPException(
            status_code=404,
            detail="Студент не найден в этой команде"
        )

        response = await async_client.patch(
            f"/teams/{any_uuid}/students/{any_uuid}",
            json={"role": "Lead"}
        )

        assert response.status_code == 404


class TestTeamMemberRemove:
    """DELETE /teams/{team_id}/students/{student_id}"""

    async def test_remove_student_success(self, async_client, mock_team_member_service, any_uuid):
        """Remove student from team."""
        mock_team_member_service.remove_student_from_team.return_value = True

        response = await async_client.delete(f"/teams/{any_uuid}/students/{any_uuid}")

        assert response.status_code == 200
        assert "удален" in response.text

    async def test_remove_student_not_found(self, async_client, mock_team_member_service, any_uuid):
        """Remove non-existent member returns 404."""
        mock_team_member_service.remove_student_from_team.return_value = False

        response = await async_client.delete(f"/teams/{any_uuid}/students/{any_uuid}")

        assert response.status_code == 404
"""Tests for meeting endpoints."""
import pytest
from uuid import UUID, uuid4
from unittest.mock import MagicMock
from datetime import datetime, timezone


class TestMeetingCreate:
    """POST /meetings/"""

    @pytest.fixture
    def create_payload(self, any_uuid):
        return {
            "name": "Sprint Planning",
            "resume": "Plan the sprint",
            "date": "2026-05-10T10:00:00+00:00",
            "team_id": str(any_uuid),
            "status": "SCHEDULED",
        }

    async def test_create_success(self, async_client, mock_meeting_service, create_payload, any_uuid):
        """Create meeting successfully."""
        mock_meeting_service.create.return_value = MagicMock(
            id=any_uuid,
            name="Sprint Planning",
            resume="Plan the sprint",
            date=datetime(2026, 5, 10, 10, 0, tzinfo=timezone.utc),
            status="SCHEDULED",
            team_id=create_payload["team_id"],
            previous_meeting_id=None,
            next_meeting_id=None,
        )

        response = await async_client.post("/meetings/", json=create_payload)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Sprint Planning"
        assert data["status"] == "SCHEDULED"

    async def test_create_duplicate_time(self, async_client, mock_meeting_service, create_payload):
        """Create meeting at same time returns 400."""
        from fastapi import HTTPException
        mock_meeting_service.create.side_effect = HTTPException(
            status_code=400,
            detail="Meeting time must be unique within the team"
        )

        response = await async_client.post("/meetings/", json=create_payload)

        assert response.status_code == 400

    async def test_create_team_not_found(self, async_client, mock_meeting_service, create_payload):
        """Create meeting for non-existent team returns 404."""
        from fastapi import HTTPException
        mock_meeting_service.create.side_effect = HTTPException(
            status_code=404,
            detail="Team not found"
        )

        response = await async_client.post("/meetings/", json=create_payload)

        assert response.status_code == 404


class TestMeetingGet:
    """GET /meetings/{id}"""

    async def test_get_by_id_success(self, async_client, mock_meeting_service, meeting_data, any_uuid):
        """Get existing meeting."""
        mock_meeting_service.get_by_id.return_value = MagicMock(**meeting_data)

        response = await async_client.get(f"/meetings/{any_uuid}")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Sprint Planning"

    async def test_get_by_id_not_found(self, async_client, mock_meeting_service, any_uuid):
        """Get non-existent meeting returns 404."""
        mock_meeting_service.get_by_id.return_value = None

        response = await async_client.get(f"/meetings/{any_uuid}")

        assert response.status_code == 404


class TestMeetingUpdate:
    """PATCH /meetings/{id}"""

    async def test_update_success(self, async_client, mock_meeting_service, meeting_data, any_uuid):
        """Update meeting successfully."""
        updated = {**meeting_data, "name": "Updated Meeting"}
        mock_meeting_service.update.return_value = MagicMock(**updated)

        response = await async_client.patch(
            f"/meetings/{any_uuid}",
            json={"name": "Updated Meeting"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Meeting"

    async def test_update_not_found(self, async_client, mock_meeting_service, any_uuid):
        """Update non-existent meeting returns 404."""
        from fastapi import HTTPException
        mock_meeting_service.update.side_effect = HTTPException(
            status_code=404,
            detail="Meeting not found"
        )

        response = await async_client.patch(
            f"/meetings/{any_uuid}",
            json={"name": "New"}
        )

        assert response.status_code == 404


class TestMeetingDelete:
    """DELETE /meetings/{id}"""

    async def test_delete_success(self, async_client, mock_meeting_service, any_uuid):
        """Delete meeting successfully."""
        mock_meeting_service.delete.return_value = True

        response = await async_client.delete(f"/meetings/{any_uuid}")

        assert response.status_code == 204

    async def test_delete_not_found(self, async_client, mock_meeting_service, any_uuid):
        """Delete non-existent meeting returns 404."""
        mock_meeting_service.delete.return_value = False

        response = await async_client.delete(f"/meetings/{any_uuid}")

        assert response.status_code == 404


class TestMeetingList:
    """GET /meetings/"""

    async def test_list_for_calendar(self, async_client, mock_meeting_service, any_uuid):
        """List meetings for calendar."""
        mock_meeting_service.get_list.return_value = MagicMock(
            total=2,
            items=[
                MagicMock(
                    id=any_uuid,
                    name="Meeting 1",
                    date=datetime(2026, 5, 10, 10, 0, tzinfo=timezone.utc),
                    status="SCHEDULED",
                    team_id=str(any_uuid),
                ),
                MagicMock(
                    id=uuid4(),
                    name="Meeting 2",
                    date=datetime(2026, 5, 17, 10, 0, tzinfo=timezone.utc),
                    status="SCHEDULED",
                    team_id=str(any_uuid),
                ),
            ]
        )

        response = await async_client.get(f"/meetings/?team_id={any_uuid}")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    async def test_list_with_date_range(self, async_client, mock_meeting_service, any_uuid):
        """List meetings with date range filter."""
        mock_meeting_service.get_list.return_value = MagicMock(
            total=1,
            items=[MagicMock()]
        )

        response = await async_client.get(
            f"/meetings/?team_id={any_uuid}&start_date=2026-05-01T00:00:00&end_date=2026-05-31T23:59:59"
        )

        assert response.status_code == 200


class TestMeetingComplete:
    """POST /meetings/{id}/complete"""

    async def test_complete_success(self, async_client, mock_meeting_service, meeting_data, any_uuid):
        """Complete meeting successfully."""
        completed = {**meeting_data, "status": "COMPLETED"}
        mock_meeting_service.complete_meeting.return_value = MagicMock(**completed)

        response = await async_client.post(f"/meetings/{any_uuid}/complete")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPLETED"

    async def test_complete_already_completed(self, async_client, mock_meeting_service, any_uuid):
        """Complete already completed meeting returns 400."""
        from fastapi import HTTPException
        mock_meeting_service.complete_meeting.side_effect = HTTPException(
            status_code=400,
            detail="Meeting is already completed"
        )

        response = await async_client.post(f"/meetings/{any_uuid}/complete")

        assert response.status_code == 400

    async def test_complete_not_found(self, async_client, mock_meeting_service, any_uuid):
        """Complete non-existent meeting returns 404."""
        from fastapi import HTTPException
        mock_meeting_service.complete_meeting.side_effect = HTTPException(
            status_code=404,
            detail="Meeting not found"
        )

        response = await async_client.post(f"/meetings/{any_uuid}/complete")

        assert response.status_code == 404


class TestMeetingCancel:
    """POST /meetings/{id}/cancel"""

    async def test_cancel_success(self, async_client, mock_meeting_service, meeting_data, any_uuid):
        """Cancel meeting successfully."""
        canceled = {**meeting_data, "status": "CANCELED"}
        mock_meeting_service.cancel_meeting.return_value = MagicMock(**canceled)

        response = await async_client.post(f"/meetings/{any_uuid}/cancel")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "CANCELED"

    async def test_cancel_completed_meeting(self, async_client, mock_meeting_service, any_uuid):
        """Cancel completed meeting returns 400."""
        from fastapi import HTTPException
        mock_meeting_service.cancel_meeting.side_effect = HTTPException(
            status_code=400,
            detail="Cannot cancel completed meeting"
        )

        response = await async_client.post(f"/meetings/{any_uuid}/cancel")

        assert response.status_code == 400


# =============================================================================
# Meeting Tasks
# =============================================================================
class TestMeetingTaskAdd:
    """POST /meetings/{meeting_id}/tasks"""

    @pytest.fixture
    def task_payload(self):
        return {
            "description": "Implement feature X",
        }

    async def test_add_task_success(self, async_client, mock_meeting_service, mock_task_service, task_payload, any_uuid):
        """Add task to meeting successfully."""
        mock_meeting_service.get_by_id.return_value = MagicMock(id=any_uuid)
        mock_task_service.create_for_meeting.return_value = MagicMock(
            id=uuid4(),
            description="Implement feature X",
            is_completed=False,
        )

        response = await async_client.post(
            f"/meetings/{any_uuid}/tasks",
            json=task_payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Implement feature X"
        assert data["is_completed"] is False

    async def test_add_task_meeting_not_found(self, async_client, mock_meeting_service, task_payload, any_uuid):
        """Add task to non-existent meeting returns 404."""
        mock_meeting_service.get_by_id.return_value = None

        response = await async_client.post(
            f"/meetings/{any_uuid}/tasks",
            json=task_payload
        )

        assert response.status_code == 404


class TestMeetingTaskAttachExisting:
    """POST /meetings/{meeting_id}/tasks/{task_id}"""

    async def test_attach_existing_success(self, async_client, mock_meeting_service, mock_task_service, any_uuid):
        """Attach existing task to meeting."""
        mock_meeting_service.get_by_id.return_value = MagicMock(id=any_uuid)
        mock_task_service.add_to_meeting.return_value = None

        response = await async_client.post(f"/meetings/{any_uuid}/tasks/{any_uuid}")

        assert response.status_code == 200
        assert "привязана" in response.json()["message"]

    async def test_attach_meeting_not_found(self, async_client, mock_meeting_service, any_uuid):
        """Attach to non-existent meeting returns 404."""
        mock_meeting_service.get_by_id.return_value = None

        response = await async_client.post(f"/meetings/{any_uuid}/tasks/{any_uuid}")

        assert response.status_code == 404


class TestMeetingTaskDetach:
    """DELETE /meetings/{meeting_id}/tasks/{task_id}"""

    async def test_detach_task_success(self, async_client, mock_task_service, any_uuid):
        """Detach task from meeting (task not deleted)."""
        mock_task_service.remove_from_meeting.return_value = None

        response = await async_client.delete(f"/meetings/{any_uuid}/tasks/{any_uuid}")

        assert response.status_code == 204

    async def test_detach_task_not_found(self, async_client, mock_task_service, any_uuid):
        """Detach non-existent task returns 404."""
        from fastapi import HTTPException
        mock_task_service.remove_from_meeting.side_effect = HTTPException(
            status_code=404,
            detail="Task not found"
        )

        response = await async_client.delete(f"/meetings/{any_uuid}/tasks/{any_uuid}")

        assert response.status_code == 404
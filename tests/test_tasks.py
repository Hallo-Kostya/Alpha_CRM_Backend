"""Tests for task endpoints."""
import pytest
from uuid import UUID, uuid4
from unittest.mock import MagicMock


class TestTaskCreate:
    """POST /tasks/"""

    @pytest.fixture
    def create_payload(self):
        return {
            "description": "Implement feature X",
        }

    async def test_create_success(self, async_client, mock_task_service, create_payload, any_uuid):
        """Create task without meeting."""
        mock_task_service.create.return_value = MagicMock(
            id=any_uuid,
            description="Implement feature X",
            is_completed=False,
        )

        response = await async_client.post("/tasks/", json=create_payload)

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Implement feature X"
        assert data["is_completed"] is False

    async def test_create_validation_error(self, async_client):
        """Empty description returns 422."""
        response = await async_client.post("/tasks/", json={})

        assert response.status_code == 422


class TestTaskCreateForMeeting:
    """POST /tasks/for-meeting/{meeting_id}"""

    @pytest.fixture
    def create_payload(self):
        return {
            "description": "Meeting task",
        }

    async def test_create_for_meeting_success(self, async_client, mock_task_service, create_payload, any_uuid):
        """Create task and attach to meeting."""
        mock_task_service.create_for_meeting.return_value = MagicMock(
            id=any_uuid,
            description="Meeting task",
            is_completed=False,
        )

        response = await async_client.post(
            f"/tasks/for-meeting/{any_uuid}",
            json=create_payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Meeting task"

    async def test_create_for_meeting_not_found(self, async_client, mock_task_service, create_payload, any_uuid):
        """Create for non-existent meeting returns 404."""
        from fastapi import HTTPException
        mock_task_service.create_for_meeting.side_effect = HTTPException(
            status_code=404,
            detail="Meeting with ID not found"
        )

        response = await async_client.post(
            f"/tasks/for-meeting/{any_uuid}",
            json=create_payload
        )

        assert response.status_code == 404


class TestTaskGet:
    """GET /tasks/{id}"""

    async def test_get_by_id_success(self, async_client, mock_task_service, task_data, any_uuid):
        """Get existing task."""
        mock_task_service.get_by_id.return_value = MagicMock(**task_data)

        response = await async_client.get(f"/tasks/{any_uuid}")

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Implement feature X"
        assert data["is_completed"] is False

    async def test_get_by_id_not_found(self, async_client, mock_task_service, any_uuid):
        """Get non-existent task returns 404."""
        mock_task_service.get_by_id.return_value = None

        response = await async_client.get(f"/tasks/{any_uuid}")

        assert response.status_code == 404
        assert "не найдена" in response.json()["detail"]


class TestTaskList:
    """GET /tasks/"""

    async def test_list_all_tasks(self, async_client, mock_task_service):
        """List all tasks."""
        mock_task_service.get_list.return_value = [
            MagicMock(id=uuid4(), description="Task 1", is_completed=False),
            MagicMock(id=uuid4(), description="Task 2", is_completed=True),
        ]

        response = await async_client.get("/tasks/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_list_filtered_by_meeting(self, async_client, mock_task_service, any_uuid):
        """List tasks filtered by meeting."""
        mock_task_service.get_list.return_value = [
            MagicMock(id=uuid4(), description="Meeting task", is_completed=False),
        ]

        response = await async_client.get(f"/tasks/?meeting_id={any_uuid}")

        assert response.status_code == 200
        mock_task_service.get_list.assert_awaited_with(any_uuid)


class TestTaskUpdate:
    """PATCH /tasks/{id}"""

    async def test_update_description(self, async_client, mock_task_service, task_data, any_uuid):
        """Update task description."""
        updated = {**task_data, "description": "Updated description"}
        mock_task_service.update.return_value = MagicMock(**updated)

        response = await async_client.patch(
            f"/tasks/{any_uuid}",
            json={"description": "Updated description"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"

    async def test_update_status(self, async_client, mock_task_service, task_data, any_uuid):
        """Update task completion status."""
        updated = {**task_data, "is_completed": True}
        mock_task_service.update.return_value = MagicMock(**updated)

        response = await async_client.patch(
            f"/tasks/{any_uuid}",
            json={"is_completed": True}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_completed"] is True

    async def test_update_not_found(self, async_client, mock_task_service, any_uuid):
        """Update non-existent task returns 404."""
        from fastapi import HTTPException
        mock_task_service.update.side_effect = HTTPException(
            status_code=404,
            detail="Task not found"
        )

        response = await async_client.patch(
            f"/tasks/{any_uuid}",
            json={"description": "New"}
        )

        assert response.status_code == 404


class TestTaskDelete:
    """DELETE /tasks/{id}"""

    async def test_delete_success(self, async_client, mock_task_service, any_uuid):
        """Delete task completely (removes from all meetings)."""
        mock_task_service.delete.return_value = True

        response = await async_client.delete(f"/tasks/{any_uuid}")

        assert response.status_code == 204

    async def test_delete_not_found(self, async_client, mock_task_service, any_uuid):
        """Delete non-existent task returns 404."""
        mock_task_service.delete.return_value = False

        response = await async_client.delete(f"/tasks/{any_uuid}")

        assert response.status_code == 404


class TestTaskMoveToNextMeeting:
    """POST /tasks/{task_id}/move-to-next-meeting"""

    async def test_move_success(self, async_client, mock_task_service, task_data, any_uuid):
        """Move incomplete task to next meeting."""
        mock_task_service.move_to_next_meeting.return_value = MagicMock(**task_data)

        response = await async_client.post(f"/tasks/{any_uuid}/move-to-next-meeting")

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Implement feature X"

    async def test_move_completed_task(self, async_client, mock_task_service, any_uuid):
        """Move completed task returns 400."""
        from fastapi import HTTPException
        mock_task_service.move_to_next_meeting.side_effect = HTTPException(
            status_code=400,
            detail="Cannot move completed task"
        )

        response = await async_client.post(f"/tasks/{any_uuid}/move-to-next-meeting")

        assert response.status_code == 400

    async def test_move_no_next_meeting(self, async_client, mock_task_service, any_uuid):
        """Move when no next meeting returns 404."""
        from fastapi import HTTPException
        mock_task_service.move_to_next_meeting.side_effect = HTTPException(
            status_code=404,
            detail="No upcoming meeting found"
        )

        response = await async_client.post(f"/tasks/{any_uuid}/move-to-next-meeting")

        assert response.status_code == 404

    async def test_move_not_attached(self, async_client, mock_task_service, any_uuid):
        """Move task not attached to any meeting returns 404."""
        from fastapi import HTTPException
        mock_task_service.move_to_next_meeting.side_effect = HTTPException(
            status_code=404,
            detail="Task is not assigned to any meeting"
        )

        response = await async_client.post(f"/tasks/{any_uuid}/move-to-next-meeting")

        assert response.status_code == 404


class TestTaskAttachToMeeting:
    """POST /tasks/{task_id}/meetings/{meeting_id}"""

    async def test_attach_success(self, async_client, mock_task_service, any_uuid):
        """Attach task to meeting."""
        mock_task_service.add_to_meeting.return_value = None

        response = await async_client.post(f"/tasks/{any_uuid}/meetings/{any_uuid}")

        assert response.status_code == 200
        assert "прикреплена" in response.json()["message"]

    async def test_attach_already_attached(self, async_client, mock_task_service, any_uuid):
        """Attach already attached task returns 400."""
        from fastapi import HTTPException
        mock_task_service.add_to_meeting.side_effect = HTTPException(
            status_code=400,
            detail="Task is already assigned to this meeting"
        )

        response = await async_client.post(f"/tasks/{any_uuid}/meetings/{any_uuid}")

        assert response.status_code == 400

    async def test_attach_task_not_found(self, async_client, mock_task_service, any_uuid):
        """Attach non-existent task returns 404."""
        from fastapi import HTTPException
        mock_task_service.add_to_meeting.side_effect = HTTPException(
            status_code=404,
            detail="Task with ID not found"
        )

        response = await async_client.post(f"/tasks/{any_uuid}/meetings/{any_uuid}")

        assert response.status_code == 404

    async def test_attach_meeting_not_found(self, async_client, mock_task_service, any_uuid):
        """Attach to non-existent meeting returns 404."""
        from fastapi import HTTPException
        mock_task_service.add_to_meeting.side_effect = HTTPException(
            status_code=404,
            detail="Meeting with ID not found"
        )

        response = await async_client.post(f"/tasks/{any_uuid}/meetings/{any_uuid}")

        assert response.status_code == 404


class TestTaskDetachFromMeeting:
    """DELETE /tasks/{task_id}/meetings/{meeting_id}"""

    async def test_detach_success(self, async_client, mock_task_service, any_uuid):
        """Detach task from meeting (task remains)."""
        mock_task_service.remove_from_meeting.return_value = None

        response = await async_client.delete(f"/tasks/{any_uuid}/meetings/{any_uuid}")

        assert response.status_code == 204

    async def test_detach_task_not_found(self, async_client, mock_task_service, any_uuid):
        """Detach non-existent task returns 404."""
        from fastapi import HTTPException
        mock_task_service.remove_from_meeting.side_effect = HTTPException(
            status_code=404,
            detail="Task with ID not found"
        )

        response = await async_client.delete(f"/tasks/{any_uuid}/meetings/{any_uuid}")

        assert response.status_code == 404

    async def test_detach_meeting_not_found(self, async_client, mock_task_service, any_uuid):
        """Detach from non-existent meeting returns 404."""
        from fastapi import HTTPException
        mock_task_service.remove_from_meeting.side_effect = HTTPException(
            status_code=404,
            detail="Meeting with ID not found"
        )

        response = await async_client.delete(f"/tasks/{any_uuid}/meetings/{any_uuid}")

        assert response.status_code == 404
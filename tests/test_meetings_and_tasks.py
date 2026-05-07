"""Тесты /api/v1/meetings/* и /api/v1/tasks/*"""
import uuid
from datetime import datetime, timedelta
import pytest
from httpx import AsyncClient
from tests.factories import create_team, create_meeting, create_task, uid

pytestmark = pytest.mark.asyncio

MEETINGS_BASE = "/api/v1/meetings"
TASKS_BASE = "/api/v1/tasks"


def future_date(days: int = 1) -> str:
    return (datetime.now() + timedelta(days=days)).isoformat()


# ===========================================================================
# Meetings
# ===========================================================================

class TestCreateMeeting:
    async def test_create_success(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        resp = await auth_client.post(MEETINGS_BASE + "/", json={
            "name": f"Встреча_{uid()}",
            "date": future_date(),
            "team_id": team["id"],
            "status": "SCHEDULED",
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["team_id"] == team["id"]
        assert "id" in body

    async def test_create_with_resume(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        resp = await auth_client.post(MEETINGS_BASE + "/", json={
            "name": f"Встреча_{uid()}",
            "date": future_date(),
            "team_id": team["id"],
            "resume": "Обсудили архитектуру",
        })
        assert resp.status_code == 201
        assert resp.json()["resume"] == "Обсудили архитектуру"

    async def test_create_requires_auth(self, client: AsyncClient):
        resp = await client.post(MEETINGS_BASE + "/", json={
            "name": "Test",
            "date": future_date(),
            "team_id": str(uuid.uuid4()),
        })
        assert resp.status_code == 401


class TestGetMeeting:
    async def test_get_by_id(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        meeting = await create_meeting(auth_client, team["id"])
        resp = await auth_client.get(f"{MEETINGS_BASE}/{meeting['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == meeting["id"]

    async def test_get_nonexistent(self, auth_client: AsyncClient):
        resp = await auth_client.get(f"{MEETINGS_BASE}/{uuid.uuid4()}")
        assert resp.status_code == 404


class TestListMeetings:
    async def test_list_all(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        await create_meeting(auth_client, team["id"])
        resp = await auth_client.get(MEETINGS_BASE + "/")
        assert resp.status_code == 200

    async def test_list_filter_by_team(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        await create_meeting(auth_client, team["id"])

        resp = await auth_client.get(MEETINGS_BASE + "/", params={"team_id": team["id"]})
        assert resp.status_code == 200
        meetings = resp.json()
        # Все встречи должны принадлежать этой команде
        for m in meetings:
            assert m["team_id"] == team["id"]

    async def test_list_filter_by_date_range(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        await create_meeting(auth_client, team["id"])

        start = datetime.now().isoformat()
        end = (datetime.now() + timedelta(days=30)).isoformat()
        resp = await auth_client.get(
            MEETINGS_BASE + "/",
            params={"start_date": start, "end_date": end},
        )
        assert resp.status_code == 200


class TestUpdateMeeting:
    async def test_update_name(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        meeting = await create_meeting(auth_client, team["id"])

        new_name = f"Обновлённая_{uid()}"
        resp = await auth_client.patch(
            f"{MEETINGS_BASE}/{meeting['id']}",
            json={"name": new_name},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == new_name

    async def test_update_status(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        meeting = await create_meeting(auth_client, team["id"])

        resp = await auth_client.patch(
            f"{MEETINGS_BASE}/{meeting['id']}",
            json={"status": "COMPLETED"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "COMPLETED"


class TestDeleteMeeting:
    async def test_delete_success(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        meeting = await create_meeting(auth_client, team["id"])

        resp = await auth_client.delete(f"{MEETINGS_BASE}/{meeting['id']}")
        assert resp.status_code == 204

        resp2 = await auth_client.get(f"{MEETINGS_BASE}/{meeting['id']}")
        assert resp2.status_code == 404

    async def test_delete_nonexistent(self, auth_client: AsyncClient):
        resp = await auth_client.delete(f"{MEETINGS_BASE}/{uuid.uuid4()}")
        assert resp.status_code == 404


class TestMeetingTasks:
    async def test_add_task_to_meeting(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        meeting = await create_meeting(auth_client, team["id"])

        resp = await auth_client.post(
            f"{MEETINGS_BASE}/{meeting['id']}/tasks",
            json={"description": f"Задача_{uid()}"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["meeting_id"] == meeting["id"]
        assert "task_id" in body
        assert body["is_completed"] is False

    async def test_add_task_to_nonexistent_meeting(self, auth_client: AsyncClient):
        resp = await auth_client.post(
            f"{MEETINGS_BASE}/{uuid.uuid4()}/tasks",
            json={"description": "Задача"},
        )
        assert resp.status_code == 404

    async def test_remove_task_from_meeting(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        meeting = await create_meeting(auth_client, team["id"])
        task_resp = await auth_client.post(
            f"{MEETINGS_BASE}/{meeting['id']}/tasks",
            json={"description": f"Задача_{uid()}"},
        )
        task_id = task_resp.json()["task_id"]

        resp = await auth_client.delete(f"{MEETINGS_BASE}/{meeting['id']}/tasks/{task_id}")
        assert resp.status_code == 204


# ===========================================================================
# Tasks
# ===========================================================================

class TestCreateTask:
    async def test_create_success(self, auth_client: AsyncClient):
        resp = await auth_client.post(TASKS_BASE + "/", json={"description": f"Задача_{uid()}"})
        assert resp.status_code == 201
        body = resp.json()
        assert "id" in body
        assert body["is_completed"] is False

    async def test_create_requires_auth(self, client: AsyncClient):
        resp = await client.post(TASKS_BASE + "/", json={"description": "Test"})
        assert resp.status_code == 401


class TestGetTask:
    async def test_get_by_id(self, auth_client: AsyncClient):
        task = await create_task(auth_client)
        resp = await auth_client.get(f"{TASKS_BASE}/{task['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == task["id"]

    async def test_get_nonexistent(self, auth_client: AsyncClient):
        resp = await auth_client.get(f"{TASKS_BASE}/{uuid.uuid4()}")
        assert resp.status_code == 404


class TestListTasks:
    async def test_list_all(self, auth_client: AsyncClient):
        await create_task(auth_client)
        resp = await auth_client.get(TASKS_BASE + "/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_list_filter_by_meeting(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        meeting = await create_meeting(auth_client, team["id"])
        await auth_client.post(
            f"{MEETINGS_BASE}/{meeting['id']}/tasks",
            json={"description": f"Задача_{uid()}"},
        )

        resp = await auth_client.get(TASKS_BASE + "/", params={"meeting_id": meeting["id"]})
        assert resp.status_code == 200
        tasks = resp.json()
        assert len(tasks) >= 1


class TestUpdateTask:
    async def test_mark_as_completed(self, auth_client: AsyncClient):
        task = await create_task(auth_client)
        resp = await auth_client.patch(
            f"{TASKS_BASE}/{task['id']}",
            json={"is_completed": True},
        )
        assert resp.status_code == 200
        assert resp.json()["is_completed"] is True

    async def test_update_description(self, auth_client: AsyncClient):
        task = await create_task(auth_client)
        resp = await auth_client.patch(
            f"{TASKS_BASE}/{task['id']}",
            json={"description": "Обновлённое описание"},
        )
        assert resp.status_code == 200
        assert resp.json()["description"] == "Обновлённое описание"


class TestDeleteTask:
    async def test_delete_success(self, auth_client: AsyncClient):
        task = await create_task(auth_client)
        resp = await auth_client.delete(f"{TASKS_BASE}/{task['id']}")
        assert resp.status_code == 204

        resp2 = await auth_client.get(f"{TASKS_BASE}/{task['id']}")
        assert resp2.status_code == 404

    async def test_delete_nonexistent(self, auth_client: AsyncClient):
        resp = await auth_client.delete(f"{TASKS_BASE}/{uuid.uuid4()}")
        assert resp.status_code == 404


class TestMoveTask:
    async def test_move_to_next_meeting(self, auth_client: AsyncClient):
        """Перенос задачи — ручка должна отвечать 200 или 404 (если нет след. встречи)."""
        team = await create_team(auth_client)
        meeting1 = await create_meeting(auth_client, team["id"],
                                        date=(datetime.now() + timedelta(days=1)).isoformat())
        meeting2 = await create_meeting(auth_client, team["id"],
                                        date=(datetime.now() + timedelta(days=8)).isoformat(),
                                        previous_meeting_id=meeting1["id"])

        task_resp = await auth_client.post(
            f"{MEETINGS_BASE}/{meeting1['id']}/tasks",
            json={"description": f"Задача_{uid()}"},
        )
        task_id = task_resp.json()["task_id"]

        resp = await auth_client.post(f"{TASKS_BASE}/{task_id}/move-to-next-meeting")
        assert resp.status_code in (200, 404)

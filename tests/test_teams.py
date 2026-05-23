"""Тесты /api/v1/teams/*"""
import uuid
import pytest
from httpx import AsyncClient
from tests.factories import create_team, create_student, uid

pytestmark = pytest.mark.asyncio

BASE = "/api/teams"


class TestCreateTeam:
    async def test_create_success(self, auth_client: AsyncClient):
        resp = await auth_client.post(BASE + "/", json={"name": f"Команда_{uid()}"})
        assert resp.status_code == 201
        body = resp.json()
        assert "id" in body
        assert "name" in body

    async def test_create_with_group_link(self, auth_client: AsyncClient):
        resp = await auth_client.post(BASE + "/", json={
            "name": f"Команда_{uid()}",
            "group_link": "https://t.me/some_group",
        })
        assert resp.status_code == 201
        assert resp.json()["group_link"] == "https://t.me/some_group"

    async def test_create_empty_name_fails(self, auth_client: AsyncClient):
        resp = await auth_client.post(BASE + "/", json={"name": ""})
        assert resp.status_code == 422

    async def test_create_requires_auth(self, client: AsyncClient):
        resp = await client.post(BASE + "/", json={"name": "Test"})
        assert resp.status_code == 401


class TestGetTeam:
    async def test_get_by_id(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        resp = await auth_client.get(f"{BASE}/{team['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == team["id"]

    async def test_get_nonexistent(self, auth_client: AsyncClient):
        resp = await auth_client.get(f"{BASE}/{uuid.uuid4()}")
        assert resp.status_code == 404


class TestListTeams:
    async def test_list_all(self, auth_client: AsyncClient):
        await create_team(auth_client)
        resp = await auth_client.get(BASE + "/")
        assert resp.status_code == 200
        body = resp.json()
        assert "total" in body
        assert "teams" in body
        assert body["total"] >= 1

    async def test_list_team_has_member_info(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        student = await create_student(auth_client)
        await auth_client.post(
            f"{BASE}/{team['id']}/students",
            json={"student_id": student["id"]},
        )
        resp = await auth_client.get(BASE + "/")
        body = resp.json()
        found = next(t for t in body["teams"] if t["id"] == team["id"])
        assert found["members_count"] >= 1


class TestUpdateTeam:
    async def test_update_name(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        new_name = f"Переименованная_{uid()}"
        resp = await auth_client.patch(
            f"{BASE}/{team['id']}",
            json={"name": new_name},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == new_name

    async def test_update_group_link(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        resp = await auth_client.patch(
            f"{BASE}/{team['id']}",
            json={"group_link": "https://t.me/new_link"},
        )
        assert resp.status_code == 200
        assert resp.json()["group_link"] == "https://t.me/new_link"


class TestDeleteTeam:
    async def test_delete_success(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        resp = await auth_client.delete(f"{BASE}/{team['id']}")
        assert resp.status_code == 204

        resp2 = await auth_client.get(f"{BASE}/{team['id']}")
        assert resp2.status_code == 404

    async def test_delete_nonexistent(self, auth_client: AsyncClient):
        resp = await auth_client.delete(f"{BASE}/{uuid.uuid4()}")
        assert resp.status_code == 404


class TestTeamMembers:
    async def test_add_student_to_team(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        student = await create_student(auth_client)

        resp = await auth_client.post(
            f"{BASE}/{team['id']}/students",
            json={"student_id": student["id"]},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["team_id"] == team["id"]
        assert body["student_id"] == student["id"]

    async def test_add_student_with_role(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        student = await create_student(auth_client)

        resp = await auth_client.post(
            f"{BASE}/{team['id']}/students",
            json={
                "student_id": student["id"],
                "role": "Лидер",
                "study_group": "ИВТ-21",
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["role"] == "Лидер"
        assert body["study_group"] == "ИВТ-21"

    async def test_update_student_role(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        student = await create_student(auth_client)

        await auth_client.post(
            f"{BASE}/{team['id']}/students",
            json={"student_id": student["id"], "role": "Участник"},
        )

        resp = await auth_client.patch(
            f"{BASE}/{team['id']}/students/{student['id']}",
            json={"role": "Разработчик", "study_group": "ИВТ-22"},
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "Разработчик"

    async def test_remove_student_from_team(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        student = await create_student(auth_client)

        await auth_client.post(
            f"{BASE}/{team['id']}/students",
            json={"student_id": student["id"]},
        )

        resp = await auth_client.delete(f"{BASE}/{team['id']}/students/{student['id']}")
        assert resp.status_code == 200

    async def test_remove_nonexistent_member(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        resp = await auth_client.delete(f"{BASE}/{team['id']}/students/{uuid.uuid4()}")
        assert resp.status_code == 404

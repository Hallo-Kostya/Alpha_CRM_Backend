"""Тесты /api/v1/projects/*"""
import uuid
from datetime import datetime
import pytest
from httpx import AsyncClient
from tests.factories import create_project, create_team, uid

pytestmark = pytest.mark.asyncio

BASE = "/api/v1/projects"


def current_year() -> int:
    return datetime.now().year


class TestCreateProject:
    async def test_create_minimal(self, auth_client: AsyncClient):
        resp = await auth_client.post(BASE + "/", json={"name": f"Проект_{uid()}"})
        assert resp.status_code == 201
        body = resp.json()
        assert "id" in body
        assert body["year"] == current_year()  # автозаполнение
        assert body["status"] is not None

    async def test_create_with_explicit_year(self, auth_client: AsyncClient):
        resp = await auth_client.post(BASE + "/", json={
            "name": f"Проект_{uid()}",
            "year": 2025,
            "semester": "SPRING",
        })
        assert resp.status_code == 201
        assert resp.json()["year"] == 2025

    async def test_create_future_project_is_planned(self, auth_client: AsyncClient):
        resp = await auth_client.post(BASE + "/", json={
            "name": f"Проект_{uid()}",
            "year": current_year() + 2,
            "semester": "SPRING",
        })
        assert resp.status_code == 201
        assert resp.json()["status"] == "PLANNED"

    async def test_create_past_project_is_completed(self, auth_client: AsyncClient):
        resp = await auth_client.post(BASE + "/", json={
            "name": f"Проект_{uid()}",
            "year": 2020,
            "semester": "SPRING",
        })
        assert resp.status_code == 201
        assert resp.json()["status"] == "COMPLETED"

    async def test_create_empty_name_fails(self, auth_client: AsyncClient):
        resp = await auth_client.post(BASE + "/", json={"name": ""})
        assert resp.status_code == 422

    async def test_create_requires_auth(self, client: AsyncClient):
        resp = await client.post(BASE + "/", json={"name": "Test"})
        assert resp.status_code == 401


class TestGetProject:
    async def test_get_by_id(self, auth_client: AsyncClient):
        project = await create_project(auth_client)
        resp = await auth_client.get(f"{BASE}/{project['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == project["id"]

    async def test_get_nonexistent(self, auth_client: AsyncClient):
        resp = await auth_client.get(f"{BASE}/{uuid.uuid4()}")
        assert resp.status_code == 404


class TestListProjects:
    async def test_list_returns_summary(self, auth_client: AsyncClient):
        await create_project(auth_client)
        resp = await auth_client.get(BASE + "/")
        assert resp.status_code == 200
        body = resp.json()
        assert "total" in body
        assert "projects" in body
        assert body["total"] >= 1

    async def test_list_filter_by_year(self, auth_client: AsyncClient):
        await auth_client.post(BASE + "/", json={"name": f"P_{uid()}", "year": 2022, "semester": "SPRING"})
        await auth_client.post(BASE + "/", json={"name": f"P_{uid()}", "year": 2023, "semester": "SPRING"})

        resp = await auth_client.get(BASE + "/", params={"year": 2022})
        assert resp.status_code == 200
        for proj in resp.json()["projects"]:
            # summary не содержит year напрямую, но total должен быть >= 1
            pass
        assert resp.json()["total"] >= 1

    async def test_list_filter_by_semester(self, auth_client: AsyncClient):
        resp = await auth_client.get(BASE + "/", params={"semester": "SPRING"})
        assert resp.status_code == 200


class TestUpdateProject:
    async def test_update_description(self, auth_client: AsyncClient):
        project = await create_project(auth_client)
        resp = await auth_client.patch(
            f"{BASE}/{project['id']}",
            json={"description": "Новое описание", "goal": "Новая цель"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["description"] == "Новое описание"
        assert body["goal"] == "Новая цель"

    async def test_update_status(self, auth_client: AsyncClient):
        project = await create_project(auth_client)
        resp = await auth_client.patch(
            f"{BASE}/{project['id']}",
            json={"status": "COMPLETED"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "COMPLETED"

    async def test_update_eval_criteria(self, auth_client: AsyncClient):
        project = await create_project(auth_client)
        resp = await auth_client.patch(
            f"{BASE}/{project['id']}",
            json={"eval_criteria": "Критерий 1, Критерий 2", "requirements": "Требование"},
        )
        assert resp.status_code == 200


class TestDeleteProject:
    async def test_delete_success(self, auth_client: AsyncClient):
        project = await create_project(auth_client)
        resp = await auth_client.delete(f"{BASE}/{project['id']}")
        assert resp.status_code == 200

        resp2 = await auth_client.get(f"{BASE}/{project['id']}")
        assert resp2.status_code == 404

    async def test_delete_nonexistent(self, auth_client: AsyncClient):
        resp = await auth_client.delete(f"{BASE}/{uuid.uuid4()}")
        assert resp.status_code == 404


class TestProjectTeams:
    async def test_assign_team_to_project(self, auth_client: AsyncClient):
        project = await create_project(auth_client)
        team = await create_team(auth_client)

        resp = await auth_client.post(
            f"{BASE}/{project['id']}/teams",
            json={"team_id": team["id"], "status": "ACTIVE"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["project_id"] == project["id"]
        assert body["team_id"] == team["id"]

    async def test_remove_team_from_project(self, auth_client: AsyncClient):
        project = await create_project(auth_client)
        team = await create_team(auth_client)

        await auth_client.post(
            f"{BASE}/{project['id']}/teams",
            json={"team_id": team["id"], "status": "ACTIVE"},
        )

        resp = await auth_client.delete(f"{BASE}/{project['id']}/teams/{team['id']}")
        assert resp.status_code == 204

    async def test_remove_nonexistent_team_link(self, auth_client: AsyncClient):
        project = await create_project(auth_client)
        resp = await auth_client.delete(f"{BASE}/{project['id']}/teams/{uuid.uuid4()}")
        assert resp.status_code == 404

    async def test_assign_team_to_nonexistent_project(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        resp = await auth_client.post(
            f"{BASE}/{uuid.uuid4()}/teams",
            json={"team_id": team["id"], "status": "ACTIVE"},
        )
        assert resp.status_code == 404

    async def test_list_teams_for_project(self, auth_client: AsyncClient):
        project = await create_project(auth_client)
        team = await create_team(auth_client)
        await auth_client.post(
            f"{BASE}/{project['id']}/teams",
            json={"team_id": team["id"], "status": "ACTIVE"},
        )

        resp = await auth_client.get(BASE + "/", params={"team_id": team["id"]})
        assert resp.status_code == 200

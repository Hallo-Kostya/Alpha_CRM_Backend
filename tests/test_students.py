"""Тесты /api/v1/students/*"""
import pytest
from httpx import AsyncClient
from tests.factories import create_student, uid

pytestmark = pytest.mark.asyncio

BASE = "/api/v1/students"


class TestCreateStudent:
    async def test_create_minimal(self, auth_client: AsyncClient):
        resp = await auth_client.post(BASE + "/", json={
            "first_name": "Алексей",
            "last_name": "Смирнов",
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["first_name"] == "Алексей"
        assert body["last_name"] == "Смирнов"
        assert "id" in body

    async def test_create_full(self, auth_client: AsyncClient):
        resp = await auth_client.post(BASE + "/", json={
            "first_name": "Мария",
            "last_name": "Козлова",
            "patronymic": "Ивановна",
            "email": f"maria_{uid()}@test.com",
            "tg_link": f"@maria_{uid()}",
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["patronymic"] == "Ивановна"

    async def test_create_empty_name_fails(self, auth_client: AsyncClient):
        resp = await auth_client.post(BASE + "/", json={
            "first_name": "",
            "last_name": "Смирнов",
        })
        assert resp.status_code == 422

    async def test_create_requires_auth(self, client: AsyncClient):
        resp = await client.post(BASE + "/", json={
            "first_name": "Иван",
            "last_name": "Тест",
        })
        assert resp.status_code == 401


class TestGetStudent:
    async def test_get_by_id(self, auth_client: AsyncClient):
        student = await create_student(auth_client)
        resp = await auth_client.get(f"{BASE}/{student['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == student["id"]

    async def test_get_nonexistent(self, auth_client: AsyncClient):
        import uuid
        resp = await auth_client.get(f"{BASE}/{uuid.uuid4()}")
        assert resp.status_code == 404

    async def test_get_invalid_uuid(self, auth_client: AsyncClient):
        resp = await auth_client.get(f"{BASE}/not-a-uuid")
        assert resp.status_code == 422


class TestListStudents:
    async def test_list_returns_students(self, auth_client: AsyncClient):
        # Создаём несколько студентов
        await create_student(auth_client)
        await create_student(auth_client)

        resp = await auth_client.get(BASE + "/")
        assert resp.status_code == 200
        body = resp.json()
        assert "total" in body
        assert "students" in body
        assert body["total"] >= 2

    async def test_list_requires_auth(self, client: AsyncClient):
        resp = await client.get(BASE + "/")
        assert resp.status_code == 401


class TestUpdateStudent:
    async def test_update_name(self, auth_client: AsyncClient):
        student = await create_student(auth_client)
        resp = await auth_client.patch(
            f"{BASE}/{student['id']}",
            json={"first_name": "Новое", "last_name": "Имя"},
        )
        assert resp.status_code == 200
        assert resp.json()["first_name"] == "Новое"

    async def test_partial_update(self, auth_client: AsyncClient):
        student = await create_student(auth_client)
        original_last = student["last_name"]
        resp = await auth_client.patch(
            f"{BASE}/{student['id']}",
            json={"first_name": "Изменено"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["first_name"] == "Изменено"
        assert body["last_name"] == original_last  # не изменилась

    async def test_update_nonexistent(self, auth_client: AsyncClient):
        import uuid
        resp = await auth_client.patch(
            f"{BASE}/{uuid.uuid4()}",
            json={"first_name": "Тест"},
        )
        assert resp.status_code == 404


class TestDeleteStudent:
    async def test_delete_success(self, auth_client: AsyncClient):
        student = await create_student(auth_client)
        resp = await auth_client.delete(f"{BASE}/{student['id']}")
        assert resp.status_code == 204

        # Проверяем что удалён
        resp2 = await auth_client.get(f"{BASE}/{student['id']}")
        assert resp2.status_code == 404

    async def test_delete_nonexistent(self, auth_client: AsyncClient):
        import uuid
        resp = await auth_client.delete(f"{BASE}/{uuid.uuid4()}")
        assert resp.status_code == 404

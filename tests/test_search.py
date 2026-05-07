"""Тесты /api/v1/search/"""
import pytest
from httpx import AsyncClient
from tests.factories import create_student, create_team, create_project

pytestmark = pytest.mark.asyncio

BASE = "/api/search"


class TestSearch:
    async def test_search_requires_auth(self, client: AsyncClient):
        resp = await client.get(BASE + "/", params={"q": "тест"})
        assert resp.status_code == 401

    async def test_search_returns_list(self, auth_client: AsyncClient):
        resp = await auth_client.get(BASE + "/", params={"q": "а"})
        assert resp.status_code == 200
        # Ожидаем список карточек
        assert isinstance(resp.json(), list)

    async def test_search_finds_student(self, auth_client: AsyncClient):
        student = await create_student(auth_client, first_name="Уникальный", last_name="Поиском")
        resp = await auth_client.get(BASE + "/", params={"q": "Уникальный"})
        assert resp.status_code == 200
        results = resp.json()
        ids = [r.get("id") for r in results]
        assert student["id"] in ids

    async def test_search_finds_team(self, auth_client: AsyncClient):
        team = await create_team(auth_client, name="УникальнаяКомандаАБВ")
        resp = await auth_client.get(BASE + "/", params={"q": "УникальнаяКомандаАБВ"})
        assert resp.status_code == 200
        results = resp.json()
        ids = [r.get("id") for r in results]
        assert team["id"] in ids

    async def test_search_finds_project(self, auth_client: AsyncClient):
        project = await create_project(auth_client, name="УникальныйПроектЖЗИ")
        resp = await auth_client.get(BASE + "/", params={"q": "УникальныйПроектЖЗИ"})
        assert resp.status_code == 200
        results = resp.json()
        ids = [r.get("id") for r in results]
        assert project["id"] in ids

    async def test_search_empty_query_fails(self, auth_client: AsyncClient):
        # q — обязательный параметр
        resp = await auth_client.get(BASE + "/")
        assert resp.status_code == 422

    async def test_search_respects_limit(self, auth_client: AsyncClient):
        # Создаём несколько сущностей с похожим именем
        for i in range(5):
            await create_student(auth_client, first_name="ЛимитТест", last_name=f"Студент{i}")

        resp = await auth_client.get(BASE + "/", params={"q": "ЛимитТест", "limit": 2})
        assert resp.status_code == 200
        assert len(resp.json()) <= 2

    async def test_search_no_results(self, auth_client: AsyncClient):
        resp = await auth_client.get(BASE + "/", params={"q": "xzqjfkwqpownvksdnfksj"})
        assert resp.status_code == 200
        assert resp.json() == []

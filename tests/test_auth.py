"""Тесты /api/v1/auth/*"""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

BASE = "/api/auth"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

import uuid

def unique_email() -> str:
    return f"user_{uuid.uuid4().hex[:8]}@test.com"

STRONG_PWD = "strongpassword1"


# ---------------------------------------------------------------------------
# /register
# ---------------------------------------------------------------------------

class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        payload = {
            "email": unique_email(),
            "password": STRONG_PWD,
            "first_name": "Мария",
            "last_name": "Иванова",
        }
        resp = await client.post(f"{BASE}/register", json=payload)
        assert resp.status_code == 201
        body = resp.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"

    async def test_register_duplicate_email(self, client: AsyncClient):
        email = unique_email()
        payload = {
            "email": email,
            "password": STRONG_PWD,
            "first_name": "Анна",
            "last_name": "Сидорова",
        }
        await client.post(f"{BASE}/register", json=payload)
        resp = await client.post(f"{BASE}/register", json=payload)
        assert resp.status_code == 409

    async def test_register_short_password(self, client: AsyncClient):
        payload = {
            "email": unique_email(),
            "password": "short",
            "first_name": "Иван",
            "last_name": "Тест",
        }
        resp = await client.post(f"{BASE}/register", json=payload)
        assert resp.status_code == 422

    async def test_register_invalid_email(self, client: AsyncClient):
        payload = {
            "email": "not-an-email",
            "password": STRONG_PWD,
            "first_name": "Иван",
            "last_name": "Тест",
        }
        resp = await client.post(f"{BASE}/register", json=payload)
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# /login
# ---------------------------------------------------------------------------

class TestLogin:
    async def test_login_success(self, client: AsyncClient):
        email = unique_email()
        payload = {
            "email": email,
            "password": STRONG_PWD,
            "first_name": "Петр",
            "last_name": "Петров",
        }
        await client.post(f"{BASE}/register", json=payload)

        resp = await client.post(
            f"{BASE}/login",
            json={"email": email, "password": STRONG_PWD},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert "refresh_token" in body

    async def test_login_wrong_password(self, client: AsyncClient):
        email = unique_email()
        await client.post(
            f"{BASE}/register",
            json={"email": email, "password": STRONG_PWD, "first_name": "A", "last_name": "B"},
        )
        resp = await client.post(
            f"{BASE}/login",
            json={"email": email, "password": "wrongpassword1"},
        )
        assert resp.status_code == 401

    async def test_login_unknown_email(self, client: AsyncClient):
        resp = await client.post(
            f"{BASE}/login",
            json={"email": "nobody@test.com", "password": STRONG_PWD},
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# /refresh
# ---------------------------------------------------------------------------

class TestRefresh:
    async def test_refresh_success(self, client: AsyncClient):
        email = unique_email()
        reg = await client.post(
            f"{BASE}/register",
            json={"email": email, "password": STRONG_PWD, "first_name": "A", "last_name": "B"},
        )
        refresh_token = reg.json()["refresh_token"]

        resp = await client.post(f"{BASE}/refresh", params={"refresh_token": refresh_token})
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_refresh_invalid_token(self, client: AsyncClient):
        resp = await client.post(f"{BASE}/refresh", params={"refresh_token": "invalid.token.here"})
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# /me
# ---------------------------------------------------------------------------

class TestMe:
    async def test_me_authenticated(self, auth_client: AsyncClient):
        resp = await auth_client.get(f"{BASE}/me")
        assert resp.status_code == 200
        body = resp.json()
        assert "id" in body
        assert "email" in body

    async def test_me_unauthenticated(self, client: AsyncClient):
        resp = await client.get(f"{BASE}/me")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# /logout
# ---------------------------------------------------------------------------

class TestLogout:
    async def test_logout_success(self, client: AsyncClient):
        email = unique_email()
        reg = await client.post(
            f"{BASE}/register",
            json={"email": email, "password": STRONG_PWD, "first_name": "A", "last_name": "B"},
        )
        tokens = reg.json()
        access = tokens["access_token"]
        refresh = tokens["refresh_token"]

        resp = await client.post(
            f"{BASE}/logout",
            params={"refresh_token": refresh},
            headers={"Authorization": f"Bearer {access}"},
        )
        assert resp.status_code == 204

    async def test_logout_double_revoke(self, client: AsyncClient):
        """Повторный logout должен вернуть 400."""
        email = unique_email()
        reg = await client.post(
            f"{BASE}/register",
            json={"email": email, "password": STRONG_PWD, "first_name": "A", "last_name": "B"},
        )
        tokens = reg.json()
        access = tokens["access_token"]
        refresh = tokens["refresh_token"]
        headers = {"Authorization": f"Bearer {access}"}

        await client.post(f"{BASE}/logout", params={"refresh_token": refresh}, headers=headers)
        resp = await client.post(f"{BASE}/logout", params={"refresh_token": refresh}, headers=headers)
        assert resp.status_code == 400

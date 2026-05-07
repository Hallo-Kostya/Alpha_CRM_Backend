"""
Фабрики тестовых данных.
Позволяют создавать сущности через API одной строкой.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Optional

from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def uid() -> str:
    return str(uuid.uuid4())[:8]


# ---------------------------------------------------------------------------
# Curator
# ---------------------------------------------------------------------------

async def create_curator(client: AsyncClient, **overrides) -> dict:
    payload = {
        "email": f"curator_{uid()}@test.com",
        "password": "password1234",
        "first_name": "Иван",
        "last_name": "Тестов",
        **overrides,
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# Student
# ---------------------------------------------------------------------------

async def create_student(client: AsyncClient, **overrides) -> dict:
    payload = {
        "first_name": "Студент",
        "last_name": f"Тест_{uid()}",
        "email": f"student_{uid()}@test.com",
        "tg_link": f"@student_{uid()}",
        **overrides,
    }
    resp = await client.post("/api/v1/students/", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# Team
# ---------------------------------------------------------------------------

async def create_team(client: AsyncClient, **overrides) -> dict:
    payload = {
        "name": f"Команда_{uid()}",
        "group_link": None,
        **overrides,
    }
    resp = await client.post("/api/v1/teams/", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------

async def create_project(client: AsyncClient, **overrides) -> dict:
    payload = {
        "name": f"Проект_{uid()}",
        "description": "Тестовое описание",
        **overrides,
    }
    resp = await client.post("/api/v1/projects/", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# Meeting
# ---------------------------------------------------------------------------

async def create_meeting(
    client: AsyncClient,
    team_id: str,
    **overrides,
) -> dict:
    payload = {
        "name": f"Встреча_{uid()}",
        "date": (datetime.now() + timedelta(days=1)).isoformat(),
        "team_id": team_id,
        "status": "SCHEDULED",
        **overrides,
    }
    resp = await client.post("/api/v1/meetings/", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

async def create_task(client: AsyncClient, **overrides) -> dict:
    payload = {
        "description": f"Задача {uid()}",
        **overrides,
    }
    resp = await client.post("/api/v1/tasks/", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()

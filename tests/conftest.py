from __future__ import annotations

import asyncio
import os
import sys
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy import NullPool

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from testcontainers.minio import MinioContainer
from testcontainers.postgres import PostgresContainer
from app.core.database import db_helper

# ---------------------------------------------------------------------------
# Postgres
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg


@pytest.fixture(scope="session")
def db_env(postgres_container: PostgresContainer) -> str:
    user = postgres_container.username
    password = postgres_container.password
    host = postgres_container.get_container_host_ip()
    port = postgres_container.get_exposed_port(5432)
    db = postgres_container.dbname
    return {
        "DB__USER": user,
        "DB__PASSWORD": password,
        "DB__HOST": host,
        "DB__PORT": str(port),
        "DB__NAME": db,
    }

@pytest.fixture(scope="session")
def db_url(db_env: dict) -> str:
    """Построить URL для SQLAlchemy из переменных окружения."""
    return f"postgresql+asyncpg://{db_env['DB__USER']}:{db_env['DB__PASSWORD']}@{db_env['DB__HOST']}:{db_env['DB__PORT']}/{db_env['DB__NAME']}"
# ---------------------------------------------------------------------------
# MinIO
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def minio_container() -> Generator[MinioContainer, None, None]:
    with MinioContainer("minio/minio:latest") as minio:
        yield minio


@pytest.fixture(scope="session")
def minio_env(minio_container: MinioContainer) -> dict:
    """Переменные окружения для S3-клиента."""
    host = minio_container.get_container_host_ip()
    port = minio_container.get_exposed_port(9000)
    return {
        "S3_ENDPOINT": f"http://{host}:{port}",
        "S3_ACCESS_KEY": minio_container.access_key,
        "S3_SECRET_KEY": minio_container.secret_key,
        "S3_BUCKET": "test-bucket",
    }


# ---------------------------------------------------------------------------
# Выставляем env ДО любого импорта app (settings читает os.environ при старте)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def set_test_env(db_env: dict, minio_env: dict):
    """Выставляет все переменные окружения до импорта app."""
    for k, v in db_env.items():
        os.environ[k] = v
    for k, v in minio_env.items():
        os.environ[k] = v
    os.environ.setdefault("HASH__ACCESS_SECRET", "test-access-secret-32-chars-long!!")
    os.environ.setdefault("HASH__REFRESH_SECRET", "test-refresh-secret-32-chars-long!")
    os.environ.setdefault("HASH__ALGORITHM", "HS256")


# ---------------------------------------------------------------------------
# Создаём таблицы через SQLAlchemy metadata — минуя Alembic env.py полностью
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables(set_test_env, db_url: str):
    from app.infrastructure.database.base import Base
    import app.infrastructure.database.models

    engine = create_async_engine(db_url, 
                                 echo=False, 
                                 poolclass=NullPool,)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        
    await engine.dispose()


# ---------------------------------------------------------------------------
# SQLAlchemy session (для прямых INSERT в тестах)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture()
async def db_session():
    async_session = async_sessionmaker(
        bind=db_helper.engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


# ---------------------------------------------------------------------------
# FastAPI app + override зависимостей
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def app(create_tables, db_url):
    """Импортирует FastAPI app после создания таблиц и выставления env."""

    db_helper.init(
        url=db_url,
        echo=False,
        is_test=True,
    )
    
    from app.main import main_app as fastapi_app
    return fastapi_app


# ---------------------------------------------------------------------------
# HTTP-клиент (неавторизованный)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture()
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c


# ---------------------------------------------------------------------------
# Авторизованный куратор + клиент
# ---------------------------------------------------------------------------

CURATOR_EMAIL = "test_curator@example.com"
CURATOR_PASSWORD = "testpassword123"
CURATOR_DATA = {
    "email": CURATOR_EMAIL,
    "password": CURATOR_PASSWORD,
    "first_name": "Тест",
    "last_name": "Куратор",
    "patronymic": None,
}


@pytest_asyncio.fixture(scope="session")
async def curator_tokens(app) -> dict:
    """Регистрирует куратора один раз, возвращает токены."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        resp = await c.post("/api/auth/register", json=CURATOR_DATA)
        # Если уже зарегистрирован — логинимся
        if resp.status_code == 409:
            resp = await c.post(
                "/api/auth/login",
                json={"email": CURATOR_EMAIL, "password": CURATOR_PASSWORD},
            )
        assert resp.status_code in (200, 201), resp.text
        return resp.json()


@pytest_asyncio.fixture()
async def auth_client(app, curator_tokens) -> AsyncGenerator[AsyncClient, None]:
    """AsyncClient с Bearer-токеном куратора."""
    headers = {"Authorization": f"Bearer {curator_tokens['access_token']}"}
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers=headers,
    ) as c:
        yield c
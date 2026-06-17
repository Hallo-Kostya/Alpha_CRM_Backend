# Alpha CRM Backend

Backend сервис для CRM-платформы Alpha. Реализован на FastAPI с асинхронным SQLAlchemy, Alembic для миграций, MinIO для хранения файлов и Prometheus / Grafana для мониторинга.

## Основные технологии

- Python 3.12
- FastAPI
- SQLAlchemy AsyncIO
- Alembic
- PostgreSQL
- MinIO
- Prometheus, Loki, Grafana
- SQLAdmin для админ-панели
- OpenAI/AI-интеграция

## Структура проекта

- `app/main.py` — точка входа приложения
- `app/api/` — API endpoints и маршруты
- `app/infrastructure/` — доступ к БД, репозитории, S3-хранилище
- `app/schemas/` — Pydantic-схемы для DTO
- `app/services/` — бизнес-логика
- `app/admin/` — админ-панель и авторизация
- `app/core/config.py` — конфигурация через переменные окружения
- `alembic/` — миграции базы данных

## Быстрый старт

1. Создайте файл `.env` в корне проекта.
2. Добавьте обязательные переменные окружения:

```env
DB__USER=
DB__PASSWORD=
DB__HOST=
DB__PORT=
DB__NAME=
S3__ACCESS_KEY=
S3__SECRET_KEY=
PGADMIN_EMAIL=
PGADMIN_PASS=
ENVIRONMENT=development
```

3. Запустите сервисы через Docker Compose:

```bash
docker compose up --build
```

4. После старта приложение будет доступно по адресу:

- API: `http://localhost:8001/api`
- Админка: `http://localhost:8001/admin`
- Метрики Prometheus: `http://localhost:8001/api/metrics`
- Проверка здоровья: `http://localhost:8001/api/health`

## Переменные окружения

Основные переменные:

- `DB__USER` — пользователь PostgreSQL
- `DB__PASSWORD` — пароль PostgreSQL
- `DB__HOST` — хост PostgreSQL
- `DB__PORT` — порт PostgreSQL
- `DB__NAME` — имя базы данных
- `S3__ACCESS_KEY` — ключ доступа MinIO
- `S3__SECRET_KEY` — секретный ключ MinIO
- `ENVIRONMENT` — режим запуска (`development` или `production`)

Дополнительные переменные можно задавать в `.env` в формате `NESTED__KEY` для соответствующих конфигураций, например `AI__API_KEY`.

## Сервисы Docker

- `backend` — FastAPI-приложение на порту `8001`
- `pg_db` — PostgreSQL на порту `5433`
- `minio` — MinIO на портах `9000` и `9001`
- `prometheus` — Prometheus на порту `9090`
- `loki` — Loki на порту `3100`
- `grafana` — Grafana на порту `3030`

## Запуск локально без Docker

Если вы хотите запустить проект локально без Docker:

```bash
poetry install
poetry run uvicorn app.main:main_app --reload --host 0.0.0.0 --port 8000
```

## Миграции базы данных

Миграции выполняются автоматически при старте контейнера через `entrypoint.sh`.
Для ручной работы используйте:

```bash
alembic upgrade head
```

## Тестирование

Запуск тестов:

```bash
pytest
```

## Примечания

- Админ-панель создается с помощью `sqladmin`.
- API роуты находятся под префиксом `/api`.
- Сервис поддерживает загрузку артефактов, управление проектами, командами, встречами и студенческими заявками.
- Конфигурация читается из `.env` и задается через `pydantic-settings`.

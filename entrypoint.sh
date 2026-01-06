#!/bin/sh

echo "Выполняются миграции..."
cd /backend
alembic upgrade head

echo "Миграции применены, запускается сервер..."
poetry run uvicorn app.main:main_app --host 0.0.0.0 --port 8000

#!/bin/sh

echo "Выполняются миграции..."
cd /backend
alembic upgrade head

echo "Миграции применены, запускается сервер..."
if [ "$ENVIRONMENT" = "development" ]; then
    echo "Запуск в режиме разработки с hot reload..."
    poetry run uvicorn app.main:main_app --host 0.0.0.0 --port 8000 --reload
else
    echo "Запуск в продакшн режиме..."
    poetry run uvicorn app.main:main_app --host 0.0.0.0 --port 8000
fi

FROM python:3.12-slim

RUN pip install poetry

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local' \
    PYTHONPATH='/backend/app'

COPY ./pyproject.toml ./poetry.lock /backend/

WORKDIR /backend

RUN /usr/local/bin/poetry install --no-root 

COPY ./app ./app
COPY ./entrypoint.sh ./entrypoint.sh
COPY ./alembic.ini .

RUN chmod +x ./entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.core.config import settings

from app.api.endpoints.projects import router as projects_router
from app.api.endpoints.students import router as students_router
from app.api.endpoints.teams import router as teams_router
from app.api.endpoints.meetings import router as meetings_router
from app.api.endpoints.tasks import router as tasks_router
from app.api.endpoints.search import router as search_router
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.artifact import router as artifacts_router
from app.api.endpoints.ai import router as ai_router

routers = APIRouter()

router_list = [
    projects_router,
    students_router,
    teams_router,
    meetings_router,
    tasks_router,
    search_router,
    auth_router,
    artifacts_router,
    ai_router,
]

for router in router_list:
    routers.include_router(router)


@routers.get("/health")
def health_check():
    return Response("App is healthy", 200)


@routers.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.core.config import settings

from app.api.v1.endpoints.curator_user import router as auth_router
from app.api.v1.endpoints.projects import router as projects_router

from app.api.v1.endpoints.teams import router as teams_router
from app.api.v1.endpoints.students import router as students_router
from app.api.v1.endpoints.meetings import router as meeting_router
from app.api.v1.endpoints.tasks import router as tasks_router

routers = APIRouter()

router_list = [
    projects_router,
    students_router,
    teams_router,
    meeting_router,
    tasks_router,
    auth_router,
]

for router in router_list:
    routers.include_router(router, prefix=settings.api.v1.prefix)


@routers.get("/health")
def health_check():
    return Response("App is healthy", 200)


@routers.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

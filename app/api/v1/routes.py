from fastapi import APIRouter, Response
from app.core.config import settings

# from app.api.v1.endpoints.curator_user import router as auth_router
from app.api.v1.endpoints.projects import router as projects_router

# from app.api.v1.endpoints.teams import router as teams_router
from app.api.v1.endpoints.students import router as students_router

routers = APIRouter()
router_list = [projects_router, students_router]

for router in router_list:
    routers.include_router(router, prefix=settings.api.v1.prefix)


@routers.get("/health")
def health_check():
    return Response("App is healthy", 200)

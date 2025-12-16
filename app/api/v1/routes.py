from fastapi import APIRouter, Response

from app.api.v1.endpoints.curator_user import router as auth_router
from api.v1.endpoints.projects import router as projects_router
from api.v1.endpoints.teams import router as teams_router

routers = APIRouter()
router_list = [auth_router, projects_router, teams_router]

for router in router_list:
    routers.include_router(router)


@routers.get("/health")
def health_check():
    return Response("App is healthy", 200)

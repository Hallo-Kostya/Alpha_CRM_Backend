from fastapi import APIRouter, Response
from app.api.v1.endpoints.auth import router as auth_router

routers = APIRouter(prefix="/v1")
router_list = [auth_router]

for router in router_list:
    routers.tags.append("/v1")
    routers.include_router(router)


@routers.get("/health")
def health_check():
    return Response("App is healthy", 200)

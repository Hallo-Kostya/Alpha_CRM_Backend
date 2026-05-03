from fastapi import FastAPI
import uvicorn
from app.admin.auth import AdminAuth
from app.api.routes import routers as v2_routers
from app.core.database import db_helper
from app.schemas.curator import Curator
from app.schemas.team import Team
from app.schemas.project import Project
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings
from app.core.middleware import PrometheusMiddleware


from sqladmin import Admin
from app.admin.setup import (
    CuratorAdmin, StudentAdmin, TeamAdmin,
    ProjectAdmin, MeetingAdmin, TaskAdmin
)

main_app = FastAPI()

main_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend.host
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

main_app.add_middleware(
    SessionMiddleware,
    secret_key=settings.hash.access_secret,
    max_age=3600,  # 1 час
)

main_app.include_router(v2_routers, prefix="/api")
main_app.add_middleware(PrometheusMiddleware)

authentication_backend = AdminAuth(secret_key=settings.hash.access_secret)
admin = Admin(
    main_app,
    db_helper.engine, 
    title="Alpha CRM Admin", 
    # authentication_backend=authentication_backend
)

# Регистрируем модели
admin.add_view(CuratorAdmin)
admin.add_view(StudentAdmin)
admin.add_view(TeamAdmin)
admin.add_view(ProjectAdmin)
admin.add_view(MeetingAdmin)
admin.add_view(TaskAdmin)

Team.model_rebuild(force=True)
Project.model_rebuild(force=True)
Curator.model_rebuild(force=True)


if __name__ == "__main__":
    uvicorn.run(main_app, host="0.0.0.0")

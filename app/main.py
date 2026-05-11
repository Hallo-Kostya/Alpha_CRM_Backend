from fastapi import FastAPI
import uvicorn
from app.admin.auth import AdminAuth
from app.api.routes import routers as v2_routers
from app.infrastructure.database.database import db_helper
from app.infrastructure.s3_storage.init import init_s3
from app.schemas.curator import Curator
from app.schemas.team import Team
from app.schemas.project import Project
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings
from app.core.middleware import PrometheusMiddleware


from sqladmin import Admin
from app.admin.setup import (
    ArtifactAdmin, ArtifactLinkAdmin, CuratorAdmin, StudentAdmin, TeamAdmin,
    ProjectAdmin, MeetingAdmin, TaskAdmin
)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):

    db_helper.init(
        url=str(settings.db.url),
        echo=settings.db.echo,
        echo_pool=settings.db.echo_pool,
        pool_size=settings.db.pool_size,
        max_overflow=settings.db.max_overflow,
    )
    
    await init_s3()
    
    authentication_backend = AdminAuth(secret_key=settings.hash.access_secret)
    admin = Admin(
        main_app,
        engine=db_helper.engine, 
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
    admin.add_view(ArtifactAdmin)
    admin.add_view(ArtifactLinkAdmin)

    yield

    await db_helper.dispose()
    
main_app = FastAPI(
    lifespan=lifespan,
)

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

Team.model_rebuild(force=True)
Project.model_rebuild(force=True)
Curator.model_rebuild(force=True)


if __name__ == "__main__":
    uvicorn.run(main_app, host="0.0.0.0")

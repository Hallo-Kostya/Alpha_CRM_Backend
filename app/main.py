from fastapi import FastAPI
import uvicorn
from app.api.v1.routes import routers as v1_routers
from app.domain.entities.persons.curator import Curator
from app.domain.entities.teams.team import Team
from app.domain.entities.projects.project import Project
from fastapi.middleware.cors import CORSMiddleware

main_app = FastAPI()

main_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

main_app.include_router(v1_routers, prefix="/api")

Team.model_rebuild(force=True)
Project.model_rebuild(force=True)
Curator.model_rebuild(force=True)


if __name__ == "__main__":
    uvicorn.run(main_app, host="0.0.0.0")

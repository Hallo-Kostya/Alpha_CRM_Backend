from fastapi import FastAPI
import uvicorn
from app.api.v1.routes import routers as v1_routers

main_app = FastAPI()

main_app.include_router(v1_routers, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(main_app, host="0.0.0.0")

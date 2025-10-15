from fastapi import FastAPI
import uvicorn
from api.v1.routes import router as v1_router

main_app = FastAPI()

main_app.include_router(v1_router, prefix='/v1')

if __name__ == "__main__":
    uvicorn.run(main_app, host="0.0.0.0")
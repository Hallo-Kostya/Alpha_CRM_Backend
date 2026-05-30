

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_curator
from app.schemas.project import ProjectCreate
from app.services.ai_service import AIService, ai_service_getter


router = APIRouter(
    prefix="/ai",
    tags=["ai_service"],
    responses={404: {"description": "AI endpoint not found"}},
    dependencies=[Depends(get_current_curator)]
)

@router.post("/auto-fill-data")
async def auto_fill(data: ProjectCreate, service: AIService = Depends(ai_service_getter)):
    return await service.auto_fill(data)

from typing import List
from fastapi import APIRouter, Depends, Query
from app.api.dependencies import get_current_curator
from app.services.search_service import SearchService, search_service_getter

router = APIRouter(
    prefix="/search",
    tags=["search"],
    dependencies=[Depends(get_current_curator)],
)

@router.get("/", summary="Умный поиск по сущностям")
async def search_entities(
    q: str = Query(..., description="Строка поиска"),
    limit: int = Query(20, description="Максимум результатов"),
    service: SearchService = Depends(search_service_getter),
):
    """Ищет по проектам, командам и студентам. Возвращает карточки для фронта."""
    return await service.search_entities(q, limit)
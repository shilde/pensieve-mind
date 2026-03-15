import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from pensieve_mind.api.dto.schemas import SearchResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["serach"])

def get_mind_service():
    from pensieve_mind.main import mind_service
    return mind_service

@router.get("", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length=1, description="Suchanfrage in natürlicher Sprache"),
    limit: int = Query(default=10, ge=1, le=100),
    collection_id: UUID | None = Query(default=None),
) -> SearchResponse:
    service = get_mind_service()
    try:
        results = service.search(query=q, limit=limit, collection_id=collection_id)
        return SearchResponse(results=results, query=q)
    except Exception as e:
        logger.exception(f"Search fehlgeschlagen für '{q}'")
        raise HTTPException(status_code=500, detail=str(e))
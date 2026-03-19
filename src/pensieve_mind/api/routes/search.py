import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from pensieve_mind.api.dto.schemas import SearchResponse
from pensieve_mind.dependencies import get_mind_service
from pensieve_mind.search.mind_service import MindService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length=1, description="Suchanfrage in natürlicher Sprache"),
    limit: int = Query(default=10, ge=1, le=100),
    collection_id: UUID | None = Query(default=None),
    service: MindService = Depends(get_mind_service),
) -> SearchResponse:
    try:
        results = service.search(query=q, limit=limit, collection_id=collection_id)
        return SearchResponse(results=results, query=q)
    except Exception as e:
        logger.exception(f"Search fehlgeschlagen für '{q}'")
        raise HTTPException(status_code=500, detail=str(e))
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from pensieve_mind.api.dto.schemas import EmbedRequest, EmbedResponse
from pensieve_mind.dependencies import get_mind_service
from pensieve_mind.search.mind_service import MindService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/embed", tags=["embed"])


@router.post("", response_model=EmbedResponse, status_code=201)
async def embed(request: EmbedRequest, service: MindService = Depends(get_mind_service)) -> EmbedResponse:
    try:
        return await service.embed(request.bookmark_id, request.url)
    except Exception as e:
        logger.exception(f"Embedding request for bookmark {request.bookmark_id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{bookmark_id}", status_code=204)
def delete_embedding(bookmark_id: UUID, service: MindService = Depends(get_mind_service)) -> None:
    try:
        service.delete(bookmark_id)
    except Exception as e:
        logger.exception(f"Delete fehlgeschlagen für {bookmark_id}")
        raise HTTPException(status_code=500, detail=str(e))
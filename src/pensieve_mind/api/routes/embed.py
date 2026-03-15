import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException

from pensieve_mind.api.dto.schemas import EmbedRequest, EmbedResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/embed", tags=["embed"])

def get_mind_service():
    import pensieve_mind.main as main_module
    if main_module.mind_service is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    return main_module.mind_service

@router.post("", response_model=EmbedResponse, status_code=201)
async def embed(request: EmbedRequest) -> EmbedResponse:
    service = get_mind_service()
    try:
        return await service.embed(request.bookmark_id, request.url)
    except Exception as e:
        logger.info(f"Embedding request for bookmark {request.bookmark_id}")
        raise HTTPException(status_code=501, detail="Not yet implemented")

@router.delete("/{bookmark_id}", status_code=204)
def delete_embedding(bookmark_id: UUID) -> None:
    service = get_mind_service()
    try:
        service.delete(bookmark_id)
    except Exception as e:
        logger.exception(f"Delete fehlgeschlagen für {bookmark_id}")
        raise HTTPException(status_code=500, detail=str(e))
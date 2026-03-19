import logging
from uuid import UUID

from pensieve_mind.api.dto.schemas import EmbedResponse, SearchResult
from pensieve_mind.embedding.embedding_service import EmbeddingService
from pensieve_mind.scraping.scraper import Scraper

logger = logging.getLogger(__name__)

class MindService:

    def __init__(self) -> None:
        self._scraper = Scraper()
        self._embedding_service = EmbeddingService()

    async def embed(self, bookmark_id: UUID, url: str) -> EmbedResponse:
        logger.info("Starte Emnbed-Pipeline für Bookmark {bookmark_id}: {url}")

        scrape_result = await self._scraper.scrape(url)

        text_parts = [
            part for part in [
                scrape_result.title,
                scrape_result.description,
                scrape_result.content,
            ]
            if part is not None
        ]
        text_to_embed = " ".join(text_parts).strip()

        if not text_to_embed:
            logger.warning(f"Kein Content für {url}, nutze URL als Fallback")
            text_to_embed = url

        payload = {
            "bookmark_id": str(bookmark_id),
            "url": url,
            "title": scrape_result.title
        }

        embedding_id = self._embedding_service.upsert(
            bookmark_id=bookmark_id,
            text=text_to_embed,
            payload=payload,
        )

        return EmbedResponse(
            bookmark_id=bookmark_id,
            embedding_id=embedding_id,
            title=scrape_result.title,
            description=scrape_result.description,
            content_snippet=scrape_result.content[:300] if scrape_result.content else None,
        )
    
    def search(
            self,
            query: str,
            limit: int = 10,
            collection_id: UUID | None = None,
    ) -> list[SearchResult]:
        results = self._embedding_service.search(
            query=query,
            limit=limit,
            collection_filter=str(collection_id) if collection_id else None,
        )
        return [SearchResult(bookmark_id=bid, score=score) for bid, score in results]
    
    def delete(self, bookmart_id: UUID) -> None:
        self._embedding_service.delete(bookmart_id)
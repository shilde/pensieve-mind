import logging
from uuid import UUID

import logging
from uuid import UUID

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue,
)
from sentence_transformers import SentenceTransformer

from pensieve_mind.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:

    def __init__(self) -> None:
        logger.info(f"Lade Embedding-Modell: {settings.embedding_model}")
        self._model = SentenceTransformer(settings.embedding_model)
        self._qdrant = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        existing = [c.name for c in self._qdrant.get_collections().collections]
        if settings.qdrant_collection not in existing:
            logger.info(f"Erstelle Qdrant Collection '{settings.qdrant_collection}'")
            self._qdrant.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=VectorParams(
                    size=settings.embedding_dimension,
                    distance=Distance.COSINE,
                ),
            )

    def embed_text(self, text: str) -> list[float]:
        return self._model.encode(text, normalize_embeddings=True).tolist()
    
    def upsert(self, bookmark_id: UUID, text: str, payload: dict) -> str:
        vector = self.embed_text(text)
        point_id = str(bookmark_id)

        self._qdrant.upsert(
            collection_name=settings.qdrant_collection,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )
        logger.info(f"Embedding gespeichert für Bookmark {bookmark_id}")
        return point_id
    
    def search(
        self,
        query: str,
        limit: int = 10,
        collection_filter: str | None = None,
    ) -> list[tuple[UUID, float]]:
        vector = self.embed_text(query)

        query_filter = None
        if collection_filter:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="collection_id",
                        match=MatchValue(value=collection_filter),
                    )
                ]
            )

        results = self._qdrant.query_points(
            collection_name=settings.qdrant_collection,
            query=vector,
            limit=limit,
            query_filter=query_filter,
        ).points

        return [(UUID(r.id), r.score) for r in results]
    
    def delete(self, bookmark_id: UUID) -> None:
        self._qdrant.delete(
            collection_name=settings.qdrant_collection,
            points_selector=[str(bookmark_id)],
        )
        logger.info(f"Embedding gelöscht für Bookmark {bookmark_id}")
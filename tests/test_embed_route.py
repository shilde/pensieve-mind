import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from pensieve_mind.api.dto.schemas import EmbedResponse

@pytest.fixture
def embed_response() -> EmbedResponse:
    return EmbedResponse(
        bookmark_id=uuid4(),
        embedding_id="test-id",
        title="Kubernetes Docs",
        description="Official K8s documentation",
        content_snippet="Kubernetes is an open-source system...",
    )

def test_embed_returns_201(client, mock_mind_service, embed_response):
    mock_mind_service.embed = AsyncMock(return_value=embed_response)

    response = client.post("/api/embed", json={
        "bookmark_id": str(embed_response.bookmark_id),
        "url": "https://kubernetes.io",
    })

    assert response.status_code == 201
    assert response.json()["title"] == "Kubernetes Docs"
    assert response.json()["embedding_id"] == "test-id"


def test_embed_invalid_url_returns_422(client):
    response = client.post("/api/embed", json={
        "bookmark_id": str(uuid4()),
        "url": "ftp://ungueltig",
    })

    assert response.status_code == 422


def test_embed_missing_fields_returns_422(client):
    response = client.post("/api/embed", json={})

    assert response.status_code == 422


def test_delete_embedding_returns_204(client, mock_mind_service):
    bookmark_id = uuid4()

    response = client.delete(f"/api/embed/{bookmark_id}")

    assert response.status_code == 204
    mock_mind_service.delete.assert_called_once_with(bookmark_id)
import pytest
from uuid import uuid4
from pensieve_mind.api.dto.schemas import SearchResult, SearchResponse


def test_search_returns_results(client, mock_mind_service):
    bookmark_id = uuid4()
    mock_mind_service.search.return_value = [
        SearchResult(bookmark_id=bookmark_id, score=0.92)
    ]

    response = client.get("/api/search", params={"q": "kubernetes deployment"})

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "kubernetes deployment"
    assert len(data["results"]) == 1
    assert data["results"][0]["score"] == pytest.approx(0.92)


def test_search_empty_query_returns_422(client):
    response = client.get("/api/search", params={"q": ""})

    assert response.status_code == 422


def test_search_missing_query_returns_422(client):
    response = client.get("/api/search")

    assert response.status_code == 422
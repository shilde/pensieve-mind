import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from uuid import uuid4

from pensieve_mind.main import app
from pensieve_mind.api.routes.embed import get_mind_service
from pensieve_mind.api.routes.search import get_mind_service as get_mind_service_search
from pensieve_mind.api.dto.schemas import EmbedResponse, SearchResult, SearchResponse
from pensieve_mind.search.mind_service import MindService


@pytest.fixture
def mock_mind_service() -> MindService:
    service = MagicMock(spec=MindService)
    return service


@pytest.fixture
def client(mock_mind_service) -> TestClient:
    app.dependency_overrides[get_mind_service] = lambda: mock_mind_service
    app.dependency_overrides[get_mind_service_search] = lambda: mock_mind_service
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
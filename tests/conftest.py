import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from pensieve_mind.main import app
from pensieve_mind.dependencies import get_mind_service
from pensieve_mind.search.mind_service import MindService


@pytest.fixture
def mock_mind_service() -> MindService:
    service = MagicMock(spec=MindService)
    return service


@pytest.fixture
def client(mock_mind_service) -> TestClient:
    app.dependency_overrides[get_mind_service] = lambda: mock_mind_service
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

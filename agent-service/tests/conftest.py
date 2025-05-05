import pytest
from unittest.mock import Mock, patch
from azure.storage.blob import BlobClient

@pytest.fixture
def mock_config():
    return {
        "version": "test_v1",
        "model": "gpt-4",
        "temperature": 0.7
    }

@pytest.fixture
def mock_blob_client(mock_config):
    mock_client = Mock(spec=BlobClient)
    mock_client.download_blob.return_value.readall.return_value = \
        json.dumps(mock_config).encode()
    return mock_client

@pytest.fixture
def test_client(mock_blob_client):
    with patch('agent_service.config_manager.BlobClient', return_value=mock_blob_client):
        from agent_service.main import app
        yield TestClient(app)

@pytest.fixture
def rate_limit_mock():
    with patch('agent_service.rate_limiter.redis') as mock:
        mock.return_value.incr.return_value = 1  # Simulate count
        yield mock

@pytest.fixture
def load_test_client():
    # Disable rate limiting for load tests
    app.dependency_overrides[get_rate_limiter] = lambda: None
    yield TestClient(app)
    app.dependency_overrides.clear()
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from src.streaming_api import app, get_manager_storage
from src.models import StreamSettings, CamType

client = TestClient(app)

@pytest.fixture(autouse=True)
def override_manager_storage():
    """
    This creates a fresh, empty storage for each test and overrides the
    app's dependency, ensuring tests are isolated from each other.
    """
    test_storage = {"manager": None}

    def get_test_manager_storage():
        return test_storage

    # Override the real dependency with our test one
    app.dependency_overrides[get_manager_storage] = get_test_manager_storage
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def settings():
    return {"cam": CamType.CAML1, "cam_path": "/dev/video0", "fps": 30, "width": 1280, "height": 720}


def test_start_stream_success(mocker, settings):
    """
    Test the happy path for starting a stream.
    """
    mock_stream_manager = MagicMock()
    mock_stream_manager.start_stream.return_value = "http://fake.stream/url"
    mocker.patch('src.streaming_api.StreamManager', return_value=mock_stream_manager)

    response = client.post("/start", json=settings)

    assert response.status_code == 200
    assert response.json() == "http://fake.stream/url"
    from src.streaming_api import StreamManager
    StreamManager.assert_called_once_with(StreamSettings(**settings))
    mock_stream_manager.start_stream.assert_called_once()


def test_start_stream_when_already_running(settings):
    """
    Test that starting a stream fails if one is already active.
    """
    app.dependency_overrides[get_manager_storage]()["manager"] = MagicMock()

    response = client.post("/start", json=settings)

    assert response.status_code == 400
    assert response.json() == {"detail": "A stream is already running."}


def test_start_stream_runtime_error(mocker, settings):
    """
    Test that a RuntimeError during stream start is handled gracefully.
    """
    mocker.patch(
        'src.streaming_api.StreamManager.start_stream',
        side_effect=RuntimeError("Failed to access camera")
    )

    response = client.post("/start", json=settings)

    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to access camera"}
    
    
def test_stop_stream_success():
    """
    Test the happy path for stopping a stream.
    """
    mock_manager = MagicMock()
    mock_manager.stop_stream.return_value = "Stream stopped successfully."
    app.dependency_overrides[get_manager_storage]()["manager"] = mock_manager

    response = client.patch("/stop")

    assert response.status_code == 200
    assert response.json() == "Stream stopped successfully."
    mock_manager.stop_stream.assert_called_once()
    assert app.dependency_overrides[get_manager_storage]()["manager"] is None


def test_stop_stream_when_not_running():
    """
    Test that stopping fails if no stream is active.
    """
    response = client.patch("/stop")

    assert response.status_code == 400
    assert response.json() == {"detail": "No active stream to stop."}
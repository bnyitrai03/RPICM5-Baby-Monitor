import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from src.config_api import app, get_camera_manager

@pytest.fixture
def mock_camera_manager():
    """Returns a mocked CameraManager dependency."""
    mock_camera = MagicMock()
    mock_camera.id = "cam1"
    mock_camera.get_data.return_value = {"id": "cam1", "controls": {}, "formats": {}}
    mock_camera.reset_all_controls.return_value = []
    mock_camera.update_controls.return_value = []

    mock_manager = MagicMock()
    mock_manager.get_all_cameras.return_value = [mock_camera.get_data.return_value]
    mock_manager.get_camera_by_id.return_value = mock_camera

    return mock_manager


@pytest.fixture
def test_client(mock_camera_manager):
    app.dependency_overrides[get_camera_manager] = lambda: mock_camera_manager
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_list_cameras(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["id"] == "cam1"


def test_get_camera_data_success(test_client):
    response = test_client.get("/cam1")
    assert response.status_code == 200
    assert response.json()["id"] == "cam1"


def test_get_camera_data_not_found(test_client, mock_camera_manager):
    mock_camera_manager.get_camera_by_id.return_value = None
    response = test_client.get("/cam1")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_reset_camera_success(test_client):
    response = test_client.patch("/cam1/reset")
    assert response.status_code == 200
    assert "reset" in response.json()


def test_reset_camera_failure(test_client, mock_camera_manager):
    mock_camera = mock_camera_manager.get_camera_by_id.return_value
    mock_camera.reset_all_controls.return_value = ["exposure"]

    response = test_client.patch("/cam1/reset")
    assert response.status_code == 500
    assert "Failed to reset" in response.json()["detail"]


def test_update_camera_controls_success(test_client):
    body = {
        "controls": {"brightness": 5}
    }
    response = test_client.patch("/cam1/controls", json=body)
    assert response.status_code == 200
    assert "updated" in response.json()


def test_update_camera_controls_failure(test_client, mock_camera_manager):
    mock_camera = mock_camera_manager.get_camera_by_id.return_value
    mock_camera.update_controls.return_value = ["contrast"]

    body = {
        "controls": {"contrast": 15}
    }
    response = test_client.patch("/cam1/controls", json=body)
    assert response.status_code == 500
    assert "couldn't be updated" in response.json()["detail"]


def test_update_camera_controls_empty(test_client):
    response = test_client.patch("/cam1/controls", json={"controls": {}})
    assert response.status_code == 400
    assert "No controls specified" in response.json()["detail"]
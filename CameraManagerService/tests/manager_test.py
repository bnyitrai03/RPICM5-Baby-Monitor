import pytest
from unittest.mock import patch, MagicMock
from src.manager import CameraManager


@pytest.fixture
def mock_discovery():
    with patch("src.manager.get_device_paths_and_names") as mock_get_paths, \
         patch("src.manager.Camera") as mock_camera_class:
        
        mock_get_paths.return_value = (
            ["/dev/video0", "/dev/video1"],
            ["platform-xhci-hcd.1-usb-0", "platform-xhci-hcd.1-usb-1"]
        )

        # Mock Camera object instances with controls/formats
        mock_cam1 = MagicMock()
        mock_cam1.controls = {"brightness": {}}
        mock_cam1.formats = {"MJPEG": {"640x480": [30]}}
        mock_cam1.get_data.return_value = {"id": "cam1"}

        mock_cam2 = MagicMock()
        mock_cam2.controls = {"contrast": {}}
        mock_cam2.formats = {"YUYV": {"1280x720": [30]}}
        mock_cam2.get_data.return_value = {"id": "cam2"}

        mock_camera_class.side_effect = [mock_cam1, mock_cam2]

        yield {
            "get_device_paths_and_names": mock_get_paths,
            "Camera": mock_camera_class,
            "cam1": mock_cam1,
            "cam2": mock_cam2
        }


def test_discover_cameras(mock_discovery):
    manager = CameraManager()

    assert len(manager.cameras) == 2
    assert "cam1" in manager.cameras
    assert "cam2" in manager.cameras


def test_discover_no_cameras(mock_discovery):
    mock_discovery["get_device_paths_and_names"].return_value = ([],[])
    manager = CameraManager()
    assert len(manager.cameras) == 0


def test_discover_invalid_camera(mock_discovery):
    mock_discovery["cam1"].formats = {}
    manager = CameraManager()
    assert len(manager.cameras) == 1
    assert "cam1" not in manager.cameras

def test_get_all_cameras(mock_discovery):
    manager = CameraManager()
    data = manager.get_all_cameras()
    assert data == [{"id": "cam1"}, {"id": "cam2"}]


def test_get_camera_by_id(mock_discovery):
    manager = CameraManager()
    cam = manager.get_camera_by_id("cam1")
    assert cam == mock_discovery["cam1"]

def test_get_invalid_camera(mock_discovery):
    manager = CameraManager()
    invalid = manager.get_camera_by_id("invalid")
    assert invalid is None
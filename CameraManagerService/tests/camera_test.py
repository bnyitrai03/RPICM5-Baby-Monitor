import pytest
from unittest.mock import patch
from src.camera import Camera


@pytest.fixture
def mock_v4l2():
    with patch("src.camera.get_controls") as mock_get_controls, \
         patch("src.camera.get_supported_formats") as mock_get_supported_formats, \
         patch("src.camera.set_control") as mock_set_control, \
         patch("src.camera.default_all_controls") as mock_default_all_controls:
        
        mock_get_controls.return_value = {
            "brightness": {"value": 5, "type": "IntegerControl"},
            "contrast": {"value": 10, "type": "IntegerControl"}
        }
        mock_get_supported_formats.return_value = {
            "MJPEG": {"640x480": [30]}
        }
        mock_set_control.return_value = True
        mock_default_all_controls.return_value = []

        yield {
            "get_controls": mock_get_controls,
            "get_supported_formats": mock_get_supported_formats,
            "set_control": mock_set_control,
            "default_all_controls": mock_default_all_controls
        }


def test_camera_initialization(mock_v4l2):
    cam = Camera("cam1", "/dev/video0", "platform-xhci-hcd.1-usb")

    assert cam.id == "cam1"
    assert cam.path == "/dev/video0"
    assert cam.name == "platform-xhci-hcd.1-usb"
    assert "brightness" in cam.controls
    assert "MJPEG" in cam.formats


def test_get_data(mock_v4l2):
    cam = Camera("cam1", "/dev/video0", "platform-xhci-hcd.1-usb")
    data = cam.get_data()

    assert data["id"] == "cam1"
    assert data["name"] == "platform-xhci-hcd.1-usb"
    assert "brightness" in data["controls"]
    assert "MJPEG" in data["formats"]


def test_update_controls_success(mock_v4l2):
    cam = Camera("cam1", "/dev/video0", "platform-xhci-hcd.1-usb")

    failed = cam.update_controls({"brightness": 7, "contrast": 8})

    assert failed == []
    assert mock_v4l2["set_control"].call_count == 2

def test_update_controls_partial_failure(mock_v4l2):
    mock_v4l2["set_control"].side_effect = [True, False]

    cam = Camera("cam1", "/dev/video0", "platform-xhci-hcd.1-usb")
    failed = cam.update_controls({"brightness": 5, "contrast": 3})

    assert failed == ["contrast"]
    assert mock_v4l2["set_control"].call_count == 2
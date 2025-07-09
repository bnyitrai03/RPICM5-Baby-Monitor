import pytest
from unittest.mock import patch, MagicMock
import src.v4l2_wrapper as v4l2


@pytest.fixture
def mock_device():
    with patch("src.v4l2_wrapper.Device") as mock_dev:
        yield mock_dev


def test_get_device_paths_and_names_path_missing():
    with patch("os.path.exists", return_value=False):
        paths, names = v4l2.get_device_paths_and_names()
        assert paths == []
        assert names == []


def test_set_control_success(mock_device):
    control = MagicMock()
    control.name = "Brightness"
    control.flags = 0
    control.minimum = 0
    control.maximum = 10

    instance = mock_device.return_value.__enter__.return_value
    instance.controls = {"Brightness": control}

    result = v4l2.set_control("dummy", "Brightness", 5)

    assert result is True
    assert control.value == 5


def test_set_control_inactive(mock_device):
    control = MagicMock()
    control.name = "Contrast"
    control.flags = v4l2.V4L2ControlFlags.INACTIVE

    instance = mock_device.return_value.__enter__.return_value
    instance.controls = {"Contrast": control}

    result = v4l2.set_control("dummy", "Contrast", 5)
    assert result is False


def test_set_control_invalid_name(mock_device):
    instance = mock_device.return_value.__enter__.return_value
    instance.controls = {}

    result = v4l2.set_control("dummy", "InvalidControl", 10)
    assert result is False


def test_empty_flag_name():
    assert v4l2._get_flag_names(0) == []
    
    
def test_inactive_and_disabled_flag():
    assert v4l2._get_flag_names(17) == ['disabled', 'inactive']
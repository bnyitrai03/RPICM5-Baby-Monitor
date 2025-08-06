from typing import Dict, Any, List
import logging
from .v4l2_wrapper import(
    get_supported_formats,
    get_controls,
    default_all_controls,
    set_control
)

logger = logging.getLogger("Camera")

class Camera:
    """Represents a single V4L2 camera device."""
    def __init__(self, cam_id: str, device_path: str, device_name: str):
        self.id : str = cam_id
        self.path : str = device_path
        self.name : str = device_name
        self.controls : Dict[str, Any] = get_controls(device_path)
        self.formats : Dict[str, Dict[str, List[int]]] = get_supported_formats(device_path)


    def get_data(self) -> Dict[str, Any]:
        """Fetches the camera's current controls and formats from the device."""
        camera_data = {
            "id": self.id,
            "path": self.path,
            "controls": self.controls,
            "formats": self.formats
        }
        return camera_data
    
    def reset_all_controls(self) -> List[str]:
        """Reset all of the control values."""
        failed_to_set = default_all_controls(self.path)
        self.controls = get_controls(self.path)
        return failed_to_set


    def update_controls(self, new_control : Dict[str, Any]) -> List[str]:
        """Update the controls given in the 'new_control' dict."""
        failed_to_set : List[str] = []
        for control_name, control_value in new_control.items():
            if set_control(self.path, control_name, control_value) is False:
                failed_to_set.append(control_name)
                
        self.controls = get_controls(self.path)
        return failed_to_set
from typing import Dict, Any, List
from .v4l2_wrapper import get_supported_formats, get_controls

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
        
        # Update config
        
        camera_data = {
            "id": self.id,
            "name": self.name,
            "controls": self.controls,
            "formats": self.formats
        }
        return camera_data
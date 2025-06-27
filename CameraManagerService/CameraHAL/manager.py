import logging
from typing import Dict, Any, List, Optional
from .camera import Camera
from .v4l2_wrapper import get_device_paths_and_names

logger = logging.getLogger("CameraManager")

class CameraManager:
    """Discovers and manages all V4L2 cameras on the system."""
    def __init__(self):
        self.cameras: Dict[str, Camera] = {}
        self.discover_cameras()

    def discover_cameras(self):
        """Discovers all connected cameras and populate the cameras list."""
        self.cameras.clear()
        
        discovered_paths, discovered_names = get_device_paths_and_names()
        if not discovered_names:
            logger.warning("No camera devices found.")
            return
        
        for i, (cam_path, cam_name) in enumerate(zip(discovered_paths, discovered_names, strict=True), 1):
            cam_id = f"cam{i}"
            camera = Camera(cam_id, cam_path, cam_name)
            if not camera.controls or not camera.formats:
                logger.error(f"{cam_id} controls or formats is missing")
                continue

            self.cameras[cam_id] = camera

    def get_all_cameras(self) -> List[Dict[str, Any]]:
        """Returns a list of all discovered cameras and their data."""
        return [cam.get_data() for cam in self.cameras.values()]
    
    def get_camera_by_id(self, cam_id: str) -> Optional[Camera]:
        """Finds a camera object by its short ID."""
        return self.cameras.get(cam_id)
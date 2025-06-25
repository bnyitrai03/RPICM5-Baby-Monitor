import logging
from fastapi import FastAPI, HTTPException, Depends
from typing import Dict, Any, List
from .CameraHAL.manager import CameraManager
from .CameraHAL.log_config import setup_logging

setup_logging()
logger = logging.getLogger("CameraConfigAPI")

# python3 -m uvicorn CameraManagerService.config_api:app --host 127.0.0.1 --port 8000
app = FastAPI(
    title="Modular Camera Configuration API",
    description="An API to discover, inspect, and configure V4L2 cameras in real-time."
)

def get_camera_manager():
    """FastAPI dependency to get a single CameraManager instance."""
    manager = CameraManager()
    yield manager

@app.get("/cameras", summary="List connected cameras", response_model=List[Dict[str, Any]])
def list_cameras(manager: CameraManager = Depends(get_camera_manager)):
    """Discovers and lists all connected cameras with their full capabilities."""
    return manager.get_all_cameras()

@app.get("/cameras/{cam_id}", summary="Get info for a specific camera", response_model=Dict[str, Any])
def get_camera_details(cam_id: str, manager: CameraManager = Depends(get_camera_manager)):
    """Returns the full details for a single camera by its short ID."""
    camera = manager.get_camera_by_id(cam_id)
    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera with ID '{cam_id}' not found.")
    logger.info(f"Successfully retrieved details for '{cam_id}'.")
    return camera.get_data()
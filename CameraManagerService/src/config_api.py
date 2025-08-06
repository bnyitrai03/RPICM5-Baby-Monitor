import logging
from fastapi import FastAPI, HTTPException, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from .manager import CameraManager
from .log_config import setup_logging

setup_logging()
logger = logging.getLogger("CameraConfigAPI")

# python3 -m uvicorn src.config_api:app --host 127.0.0.1 --port 8000
app = FastAPI(
    title="Camera Configuration API",
    description="An API to discover and configure V4L2 cameras."
)

class ControlData(BaseModel):
    cam_id: str
    controls: Dict[str, Any]

def get_camera_manager():
    """FastAPI dependency to get a single CameraManager instance."""
    manager = CameraManager()
    yield manager


@app.get("/", summary="List connected cameras", response_model=List[Dict[str, Any]])
def list_cameras(manager: CameraManager = Depends(get_camera_manager)):
    """Discovers and lists all connected cameras with their full capabilities."""
    return manager.get_all_cameras()


@app.get("/{cam_id}", summary="Get all info for a specific camera", response_model=Dict[str, Any])
def get_camera_data(cam_id: str, manager: CameraManager = Depends(get_camera_manager)):
    """Returns the full details for a single camera by its short ID."""
    camera = manager.get_camera_by_id(cam_id)
    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera with ID '{cam_id}' not found.")
    return camera.get_data()


@app.put("/{cam_id}/reset", summary="Resets all controls to default values", response_model=ControlData)
def reset_camera(cam_id: str, manager: CameraManager = Depends(get_camera_manager)):
    """Finds a camera by its ID and resets its controls to their default values."""
    camera = manager.get_camera_by_id(cam_id)
    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera with ID '{cam_id}' not found.")
    
    failed_to_reset = camera.reset_all_controls()
    
    if failed_to_reset:
        raise HTTPException(status_code=500, detail=f"Failed to reset controls: {failed_to_reset}")
    else:
        return {"cam_id": cam_id, "controls": camera.controls}


@app.put("/{cam_id}/controls", summary="Change the controls of a specific camera", response_model=ControlData)
def update_camera_controls(cam_id: str, control_update: ControlData, manager: CameraManager = Depends(get_camera_manager)):
    """Update the given camera's control values"""
    camera = manager.get_camera_by_id(cam_id)
    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera with ID '{cam_id}' not found.")
    
    if not control_update.controls:
        raise HTTPException(status_code=400, detail="No controls specified for update.")
    
    failed_to_update = camera.update_controls(control_update.controls)
    
    if failed_to_update:
        raise HTTPException(status_code=500, detail=f"These controls couldn't be updated: {failed_to_update}")
    else:
        return {"cam_id": cam_id, "controls": camera.controls}
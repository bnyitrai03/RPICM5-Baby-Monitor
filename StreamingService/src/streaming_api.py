import logging
from fastapi import FastAPI, HTTPException, Depends
from .log_config import setup_logging
from .manager import StreamManager
from .models import StreamSettings, get_manager_storage

setup_logging()
logger = logging.getLogger("StreamingAPI")

# python3 -m uvicorn src.streaming_api:app --host 127.0.0.1 --port 8002
app = FastAPI(
    title="Camera Streaming API",
    description="An API to configure and watch V4L2 camera streams."
)

@app.post("/start", response_model=str)
def start_stream(settings: StreamSettings, manager_storage = Depends(get_manager_storage)):
    """Configure and start the streaming processes for a specific camera."""
    if manager_storage["manager"] is not None:
        raise HTTPException(status_code=400, detail="A stream is already running.")

    stream_manager = StreamManager(settings)
    try:
        url = stream_manager.start_stream()
        manager_storage["manager"] = stream_manager
        return url
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/stop", response_model=str)
def stop_stream(manager_storage = Depends(get_manager_storage)):
    stream_manager: StreamManager = manager_storage["manager"]
    if stream_manager is None:
        raise HTTPException(status_code=400, detail="No active stream to stop.")

    try:
        return stream_manager.stop_stream()
    finally:
        manager_storage["manager"] = None
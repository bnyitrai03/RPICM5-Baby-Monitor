import logging
from fastapi import FastAPI, HTTPException
from .log_config import setup_logging
from .StreamLL.manager import StreamManager
from .StreamLL.models import StreamSettings, CamType

setup_logging()
logger = logging.getLogger("StreamingAPI")

# python3 -m uvicorn StreamingService.streaming_api:app --host 127.0.0.1 --port 8002
app = FastAPI(
    title="Camera Streaming API",
    description="An API to configure and watch V4L2 camera streams."
)

@app.post("/start", response_model=str)
def start_stream(settings: StreamSettings):
    """Configure and start the streaming processes for a specific camera."""
    try:
        manager = StreamManager(settings)
        stream_url = manager.start_stream()
        return stream_url
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stop")
def stop_stream(cam_id: CamType):
    """Stop all streaming processes for a specific camera."""
    manager = StreamManager()
    result = manager.stop_stream(cam_id)
    return result
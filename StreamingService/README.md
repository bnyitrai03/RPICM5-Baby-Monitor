# StreamingService

A FastAPI-based camera streaming service that manages V4L2 stereo camera setups. The service provides REST API endpoints to start and stop camera streams with automatic video processing pipeline management.

## Features

- **Stereo camera processing**: Automatically splits stereo feeds into mono streams
- **Video pipeline management**: Manages ffmpeg and ustreamer processes for streaming
- **REST API**: Simple HTTP endpoints for stream control

## Architecture

The service consists of three main components:

1. **StreamingAPI** (`streaming_api.py`): FastAPI application providing REST endpoints
2. **StreamManager** (`manager.py`): Core logic for managing video processing pipelines
3. **Models** (`models.py`): Data models and shared state management

### Video Processing Pipeline

For each camera stream, the service creates a 3-stage pipeline:

1. **Proxy Stage**: ffmpeg captures raw MJPEG from camera and forwards to virtual device
2. **Split Stage**: ffmpeg crops stereo feed to mono (left or right eye)
3. **Stream Stage**: ustreamer serves the processed video over HTTP

## Usage

### Starting the API Server

```bash
python3 -m uvicorn src.streaming_api:app --host 127.0.0.1 --port 8002
```

### API Endpoints

#### Start Stream

**POST** `/start`

Start a camera stream with specified settings.

**Request Body:**
```json
{
  "cam": "caml1",
  "cam_path": "/dev/v4l/by-id/usb-3D_USB_Camera_3D_USB_Camera_01.00.00-video-index0",
  "fps": 30,
  "width": 3840,
  "height": 1080
}
```

**Response:**
```json
"http://rpicm5/stream/caml1/stream"
```

#### Stop Stream

**PUT** `/stop`

Stop the currently running stream.

**Response:**
```json
"Stopped stream for caml1"
```

### Camera Types

| Camera | Port | Proxy Device | Output Device | Description |
|--------|------|--------------|---------------|-------------|
| CAMR1  | 8003 | /dev/video10 | /dev/video11  | Right eye camera 1 |
| CAML1  | 8004 | /dev/video10 | /dev/video12  | Left eye camera 1 |
| CAMR2  | 8005 | /dev/video14 | /dev/video15  | Right eye camera 2 |
| CAML2  | 8006 | /dev/video14 | /dev/video16  | Left eye camera 2 |

## Dependencies

- **FastAPI**: Web framework for building APIs
- **uvicorn**: ASGI server for running FastAPI
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mock utilities for testing
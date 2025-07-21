# Service API Endpoints

This document provides a comprehensive collection of API endpoints across three services: SensorService, CameraManagerService, and StreamingService.

## Service Overview

| Service | Port | Base URL | Description |
|---------|------|----------|-------------|
| **SensorService** | 8001 | `https://rpicm5/sensors` | Temperature and light sensor monitoring |
| **CameraManagerService** | 8000 | `https://rpicm5/cameras` | V4L2 camera discovery and configuration |
| **StreamingService** | 8002 | `https://rpicm5/stream/config` | Camera streaming management |

---

## SensorService Endpoints

**Base URL:** `https://rpicm5/sensors`

### GET `/`
Get current sensor readings and configuration.

**Response:**
```json
{
  "lux_value": 245.6,
  "temp_value": 23.45,
  "lux_threshold": 100,
  "timestamp": "2025-01-15T14:30:25.123456"
}
```

### PATCH `/lux_threshold`
Update the light threshold value for LED control.

**Request Body:**
```json
150
```

**Response:**
```json
"Threshold set"
```

---

## CameraManagerService Endpoints

**Base URL:** `https://rpicm5/cameras`

### GET `/cameras`
List all connected cameras with their full capabilities.

**Response:**
```json
[
  {
    "id": "cam1",
    "name": "platform-xhci-hcd.1-usb-0:1.3:1.0-video-index0",
    "controls": {
      "brightness": {
        "value": 0,
        "default": 0,
        "type": "IntegerControl",
        "flags": [],
        "min": -64,
        "max": 64,
        "step": 1
      },
      "contrast": {
        "value": 32,
        "default": 32,
        "type": "IntegerControl",
        "flags": [],
        "min": 0,
        "max": 64,
        "step": 1
      }
    },
    "formats": {
      "YUYV": {
        "3840x1080": [1],
        "1600x600": [10, 5]
      },
      "MJPG": {
        "1920x1080": [30, 15, 10, 5]
      }
    }
  }
]
```

### GET `/cameras/{cam_id}`
Get detailed information for a specific camera.

**Parameters:**
- `cam_id` (path): Camera identifier (e.g., "cam1", "cam2")

**Response:**
```json
{
  "id": "cam1",
  "name": "platform-xhci-hcd.1-usb-0:1.3:1.0-video-index0",
  "controls": {
    "brightness": {
      "value": 0,
      "default": 0,
      "type": "IntegerControl",
      "flags": [],
      "min": -64,
      "max": 64,
      "step": 1
    }
  },
  "formats": {
    "YUYV": {
      "3840x1080": [1],
      "1600x600": [10, 5]
    }
  }
}
```

### PATCH `/cameras/{cam_id}/controls`
Update camera control values.

**Parameters:**
- `cam_id` (path): Camera identifier

**Request Body:**
```json
{
  "controls": {
    "brightness": 50,
    "contrast": 32,
    "saturation": 60,
    "exposure_auto": 1,
    "exposure_absolute": 300
  }
}
```

**Response:**
```json
{
  "message": "Controls updated successfully"
}
```

### PATCH `/cameras/{cam_id}/reset`
Reset all camera controls to their default values.

**Parameters:**
- `cam_id` (path): Camera identifier

**Response:**
```json
{
  "message": "Camera controls reset to defaults"
}
```

---

## StreamingService Endpoints

**Base URL:** `https://rpicm5/stream/config`

### POST `/start`
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
"https://rpicm5/stream/caml1/stream"
```

### PATCH `/stop`
Stop the currently running stream.

**Response:**
```json
"Stopped stream for caml1"
```

---

## Camera Stream Configuration

### Supported Camera Types

| Camera ID | Port | Proxy Device | Output Device | Description |
|-----------|------|--------------|---------------|-------------|
| **CAMR1** | 8003 | /dev/video10 | /dev/video11 | Right eye camera 1 |
| **CAML1** | 8004 | /dev/video10 | /dev/video12 | Left eye camera 1 |
| **CAMR2** | 8005 | /dev/video14 | /dev/video15 | Right eye camera 2 |
| **CAML2** | 8006 | /dev/video14 | /dev/video16 | Left eye camera 2 |

### Stream Access URLs
After starting a stream, access the video feed at:
```
https://rpicm5/stream/{camera_id}/stream
```

Examples:
- `https://rpicm5/stream/caml1/stream`
- `https://rpicm5/stream/camr1/stream`
- `https://rpicm5/stream/caml2/stream`
- `https://rpicm5/stream/camr2/stream`

---

# Service API Endpoints

This document provides a comprehensive collection of API endpoints across three services: SensorService, CameraManagerService, and StreamingService.

## Service Overview

| Service | Port | Base URL | Description |
|---------|------|----------|-------------|
| **CameraManagerService** | 8000 | `https://{HOSTNAME}/cameras` | V4L2 camera discovery and configuration |
| **SensorService** | 8001 | `https://{HOSTNAME}/sensors` | Temperature and light sensor monitoring |
| **StreamingService** | 8002 | `https://{HOSTNAME}/stream/config` | Camera streaming management |

---

All services are accessible through **nginx** proxy at `https://{HOSTNAME}/`.

## SensorService Endpoints

**Base URL:** `https://{HOSTNAME}/sensors`

### GET `/`
Get current sensor readings and configuration.

**Response:**
```json
{
  "lux_value": 245.6,
  "temp_value": 23.45,
  "lux_threshold": 100,
  "led_brightness": 0.5,
  "timestamp": "2025-08-15T14:30:25.123456"
}
```

### PUT `/lux_threshold`
Update the light threshold value for LED control.

**Request Body:**
```json
{
  "threshold": 150
}
```

**Response:**
```json
"Lux threshold set to 150"
```

#### PUT /led_brightness
Updates the LED brightness level (0.0 to 1.0).

**Request Body:**
```json
{
  "brightness": 0.8
}
```

**Response:**
```json
"LED brightness set to 0.8"
```

---

## CameraManagerService Endpoints

**Base URL:** `https://{HOSTNAME}/cameras`

### GET `/`
List all connected cameras with their full capabilities.

**Response:**
```json
[
  {
    "id": "cam1",
    "path": "/dev/v4l/by-path/platform-xhci-hcd.1-usb-0:1.3:1.0-video-index0",
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
  "path": "/dev/v4l/by-path/platform-xhci-hcd.1-usb-0:1.3:1.0-video-index0",
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

### PUT `/cameras/{cam_id}/controls`
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
  "cam_id": "cam1",
  "controls": {
    "brightness": {
      "value": 50,
      "default": 0,
      "type": "IntegerControl",
      "flags": [],
      "min": -64,
      "max": 64,
      "step": 1
    },
  }
}
```

### PUT `/cameras/{cam_id}/reset`
Reset all camera controls to their default values.

**Parameters:**
- `cam_id` (path): Camera identifier

**Response:** Camera data with controls reset to defaults.

---

## StreamingService Endpoints

**Base URL:** `https://{HOSTNAME}/stream/config`

### POST `/start`
Start a camera stream with specified settings.

**Request Body:**
```json
{
  "cam": "caml1",
  "cam_path": "/dev/v4l/by-path/platform-xhci-hcd.1-usb-0:1.1:1.0-video-index0",
  "fps": 30,
  "width": 3840,
  "height": 1080
}
```

**Response:**
```json
"https://{HOSTNAME}/stream/caml1/stream"
```

### PUT `/stop`
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
https://{HOSTNAME}/stream/{camera_id}/stream
```

Examples:
- `https://{HOSTNAME}/stream/caml1/stream`
- `https://{HOSTNAME}/stream/camr1/stream`
- `https://{HOSTNAME}/stream/caml2/stream`
- `https://{HOSTNAME}/stream/camr2/stream`

---

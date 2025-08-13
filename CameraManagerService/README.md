# Camera Manager Service

A FastAPI-based service for discovering, managing, and configuring V4L2 cameras on Linux systems. This service provides a RESTful API to interact with USB cameras, allowing you to query their capabilities, adjust controls, and reset settings.

## Features

- **Automatic Camera Discovery**: Automatically detects all connected V4L2-compatible cameras
- **Real-time Configuration**: Adjust camera controls (brightness, contrast, exposure, etc.) in real-time
- **Format Support**: Query supported pixel formats, resolutions, and frame rates
- **Control Management**: View current control values, ranges, and reset to defaults
- **RESTful API**: Clean HTTPS endpoints for integration with other applications

## Usage

### Starting the Service

```bash
python3 -m uvicorn CameraManagerService.config_api:app --host 127.0.0.1 --port 8000
```

## API Endpoints

### GET `/`
Lists all connected cameras with their full capabilities.

**Response**: Array of camera objects with ID, name, controls, and supported formats.
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
      }
    },
    "formats": {
      "YUYV": {
        "3840x1080": [1],
        "1600x600": [10, 5]
      },
      "MJPEG" : {
        "3840x1080": [60, 30, 15, 10]
      }
    }
  },
  {
    "id": "cam2"
  }
]
```

### GET `/{cam_id}`
Get detailed information for a specific camera.

**Parameters**:
- `cam_id`: Camera identifier (e.g., "cam1", "cam2")

**Response**: Camera object with controls and format information.
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
      },
      "MJPEG" : {
        "3840x1080": [60, 30, 15, 10]
      }
    }
}
```

### PUT `/{cam_id}/controls`
Update camera control values.

**Parameters**:
- `cam_id`: Camera identifier (e.g., "cam1", "cam2")
- **Body**: JSON object with control names and values
  ```json
  {
    "controls": {
      "brightness": 50,
      "contrast": 32,
      "saturation": 60
    }
  }
  ```

**Response**: Updated camera data with new control values.
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

### PUT `/{cam_id}/reset`
Reset all camera controls to their default values.

**Parameters**:
- `cam_id`: Camera identifier (e.g., "cam1", "cam2")

**Response**: Camera data with controls reset to defaults.

## Architecture

### Hardware Abstraction Layer (HAL)
- **Camera**: Represents individual camera devices with their controls and formats
- **CameraManager**: Handles device discovery and management  
- **V4L2Wrapper**: Low-level interface to V4L2 devices using linuxpy

### API Layer
- **FastAPI Application**: RESTful endpoints for camera operations
- **Pydantic Models**: Request/response validation and serialization

## Control Types

The service supports various V4L2 control types:

- **IntegerControl**: Numeric controls with min/max ranges (brightness, contrast, etc.)
- **BooleanControl**: On/off controls 
- **MenuControl**: Selection from predefined options

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI applications
- **linuxpy**: Python interface to Linux V4L2 devices
- **Pydantic**: Data validation and serialization
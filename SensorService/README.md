# SensorService

A Python-based sensor monitoring service that provides real-time temperature and light level readings through a REST API. The service interfaces with VEML7700 light sensor and MCP9800 temperature sensor using the MCP2221 USB-to-I2C bridge.

## Features

- **Real-time monitoring** of temperature and light levels
- **REST API** for accessing sensor data
- **Configurable light threshold** for LED control

## Hardware Requirements

- MCP2221 USB-to-I2C bridge
- VEML7700 ambient light sensor (I2C address: 0x10)
- MCP9800 temperature sensor (I2C address: 0x48)
- LED connected to MCP2221 GPIO pin 3

## Dependencies

- `EasyMCP2221` - Interface for MCP2221 USB-to-I2C bridge
- `hidapi` - HID API library for USB communication
- `fastapi` - Modern web framework for building APIs
- `uvicorn` - ASGI server for running FastAPI applications

## Usage

### Starting the Service

Run the FastAPI server:

```bash
python3 -m uvicorn src.sensor_api:app --host 127.0.0.1 --port 8001
```

### API Endpoints

#### GET /
Returns current sensor readings and configuration.

**Response:**
```json
{
  "lux_value": 245.6,
  "temp_value": 23.45,
  "lux_threshold": 100,
  "timestamp": "2025-01-15T14:30:25.123456"
}
```

#### PATCH /lux_threshold
Updates the light threshold value for LED control.

**Request Body:**
```json
150
```

**Response:**
```json
"Threshold set"
```

## Sensor Specifications

### VEML7700 Light Sensor
- **Resolution:** 0.0672 lux per count
- **Integration Time:** 100ms
- **Gain:** 1x
- **I2C Address:** 0x10

### MCP9800 Temperature Sensor
- **Resolution:** 12-bit (0.0625°C per count)
- **Temperature Range:** -55°C to +125°C
- **I2C Address:** 0x48

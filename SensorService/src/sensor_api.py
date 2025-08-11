import logging
from fastapi import FastAPI, HTTPException
from .log_config import setup_logging
from .sensor_controller import SensorController
from .models import SensorData, LuxThreshold, LedBrightness

setup_logging()
logger = logging.getLogger("StreamingAPI")

# Initialize singleton and start monitoring
sensor_controller = SensorController()
sensor_controller.start_monitoring()

# python3 -m uvicorn src.sensor_api:app --host 127.0.0.1 --port 8001
app = FastAPI(
    title="Sensor Manager API",
    description="An API to monitor the sensor values."
)


@app.get("/", response_model=SensorData)
def get_sensor_values():
    if sensor_controller.mcp is None:
        raise HTTPException(status_code=500, detail=f"Sensors are not connected")
    return sensor_controller.get_sensor_data()

@app.put("/lux_threshold", response_model=str) 
def set_lux_threshold_value(new_lux: LuxThreshold):
   return sensor_controller.set_lux_threshold(new_lux.threshold)

@app.put("/led_brightness", response_model=str)
def set_led_brightness(new_brightness: LedBrightness):
    return sensor_controller.set_led_brightness(new_brightness.brightness)
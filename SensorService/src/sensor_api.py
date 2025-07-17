import logging
from fastapi import FastAPI
from .log_config import setup_logging

setup_logging()
logger = logging.getLogger("StreamingAPI")

# python3 -m uvicorn src.streaming_api:app --host 127.0.0.1 --port 8001
app = FastAPI(
    title="Sensor Manager API",
    description="An API to monitor the sensor values."
)


@app.get("/light", response_model=str)
def get_lux_value():
    return ""


@app.get("/temperature", response_model=str)
def get_temp_value():
    return ""
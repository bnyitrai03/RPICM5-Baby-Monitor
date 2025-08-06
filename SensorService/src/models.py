from pydantic import BaseModel
from datetime import datetime

class SensorData(BaseModel):
    lux_value: float = -1
    temp_value: float = 0
    lux_threshold: int = 100
    timestamp: datetime | None = None


class LuxThreshold(BaseModel):
    threshold: int = 100
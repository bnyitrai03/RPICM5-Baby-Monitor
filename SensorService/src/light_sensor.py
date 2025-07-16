import EasyMCP2221
import logging

logger = logging.getLogger("LightSensor")

class LightSensor():
    """VEML7700 Light Sensor"""
    
    # Constants
    ADDR = 0x10
    CMD_ALS_CONF_0 = 0x00
    CMD_ALS_DATA = 0x04
    ALS_GAIN_x1 = 0b00
    ALS_IT_100ms = 0b0000
    ALS_POWER_ON = 0b0
    RESOLUTION_LX_PER_COUNT = 0.0672
    
    def __init__(self, mcp_device: EasyMCP2221.Device):
        self.mcp = mcp_device
        self.sensor = self.mcp.I2C_Slave(self.ADDR)
        
        # Configure sensor
        config_word = (self.ALS_GAIN_x1 << 11) | (self.ALS_IT_100ms << 6) | self.ALS_POWER_ON
        config_bytes = config_word.to_bytes(2, 'little')
        self.sensor.write_register(self.CMD_ALS_CONF_0, config_bytes)
        logger.info(f"VEML7700 initialized at address 0x{self.ADDR:02x}")

    
    def read(self) -> float:
        """Read light sensor data"""
        if not self.sensor:
            raise RuntimeError("Sensor not initialized")
        
        raw_bytes = self.sensor.read_register(self.CMD_ALS_DATA, length=2)
        raw_lux = int.from_bytes(raw_bytes, 'little')
        return round(raw_lux * self.RESOLUTION_LX_PER_COUNT)
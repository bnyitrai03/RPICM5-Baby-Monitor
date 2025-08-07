import EasyMCP2221
import logging

logger = logging.getLogger("TempSensor")

class TempSensor():
    """MCP9800 Temperature Sensor"""

    ADDR = 0x48
    CMD_TEMP_READ = 0x00
    CMD_TEMP_CONFIG = 0x01
    TEMP_RES_12_BIT = 0b01100000
    TEMP_DEGREES_C_PER_COUNT = 0.0625
    
    def __init__(self, mcp_device: EasyMCP2221.Device):
        self.mcp = mcp_device
        self.sensor = self.mcp.I2C_Slave(addr=self.ADDR, speed=400000)
        
        raw_config = self.sensor.read_register(self.CMD_TEMP_CONFIG, length=1)
        config = int.from_bytes(raw_config, 'big')
        config = config | self.TEMP_RES_12_BIT
        self.sensor.write_register(self.CMD_TEMP_CONFIG, config)
        logger.info(f"MCP9800 initialized at address 0x{self.ADDR:02x}")
    
    def read(self) -> float:
        """Read temperature sensor data"""
        if not self.sensor:
            raise RuntimeError("Sensor not initialized")
        
        try:
            raw_bytes = self.sensor.read_register(self.CMD_TEMP_READ, length=2)
            raw_16bit = int.from_bytes(raw_bytes, 'big')
            temp_12bit = raw_16bit >> 4
            
            # Sign extension for 12-bit value
            if temp_12bit > 0x7FF:
                signed_value = ~temp_12bit + 1
            else:
                signed_value = temp_12bit
            return round(signed_value * self.TEMP_DEGREES_C_PER_COUNT, 2)
        
        except Exception as e:
            logger.error(f"Error reading temperature sensor: {e}")
            raise

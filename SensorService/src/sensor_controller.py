import EasyMCP2221
import logging
import threading
import time
from datetime import datetime
from .light_sensor import LightSensor
from .temp_sensor import TempSensor
from .models import SensorData

logger = logging.getLogger("SensorController")

class SensorController:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance


    def __init__(self):
        if self._initialized:
            return
            
        self.mcp = EasyMCP2221.Device()
        self.mcp.set_pin_function(gp3="GPIO_OUT")
        
        self.light = LightSensor(self.mcp)
        self.temp = TempSensor(self.mcp)
        
        self.data = SensorData()
        self.data_lock = threading.Lock()
        
        self._initialized = True
       
       
    def get_sensor_data(self) -> SensorData:
        """"Returns the measurement data with a timestamp"""
        with self.data_lock:
            return self.data
        

    def set_lux_threshold(self, value: int) -> str:
        """"Changes the threshold for turning on the LEDs"""
        if 0 < value:
            with self.data_lock:
                self.data.lux_threshold = value
            return "Threshold set"
        else:
            logger.error(f"Invalid lux threshold: {value}")
            return f"Invalid lux threshold: {value}"
       
        
    def start_monitoring(self) -> None:
        """Start continuous monitoring in background thread"""
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()

 
    def _monitor_loop(self) -> None:
        """Continuous monitoring and controling loop"""
        while True:
            try:
                luminosity = self.light.read()
                temperature = self.temp.read()
                
                # Control LED
                #if luminosity < self.data.lux_threshold:
                    #self.mcp.GPIO_write(gp3=True)
                #else:
                    #self.mcp.GPIO_write(gp3=False)
                
                with self.data_lock:
                    self.data.lux_value = luminosity
                    self.data.temp_value = temperature
                    self.data.timestamp = datetime.now()
                
            except Exception as e:
                logger.error(f"Error in the sensor monitor loop: {e}")
            
            finally:
                time.sleep(1)
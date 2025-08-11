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
        self.mcp = None
        self.light = None
        self.temp = None
        self._initialize_hardware()
        
        self.hysteresis = 10
        self.dac_on = False
        self.brightness_changed = False
        self.data = SensorData()
        self.data_lock = threading.Lock()
       
       
    def get_sensor_data(self) -> SensorData:
        """"Returns the measurement data with a timestamp"""
        with self.data_lock:
            return self.data
        

    def set_lux_threshold(self, value: int) -> str:
        """"Changes the threshold for turning on the LEDs"""
        if 0 < value:
            with self.data_lock:
                self.data.lux_threshold = value
            return f"Lux threshold set to {value}"
        else:
            logger.error(f"Invalid lux threshold: {value}")
            return f"Invalid lux threshold: {value}"
    
    def set_led_brightness(self, value: float) -> str:
        """"Changes the brightness of the LEDs"""
        if 0 <= value <= 1:
            with self.data_lock:
                self.data.led_brightness = value
                self.brightness_changed = True
            return f"LED brightness set to {value}"
        else:
            logger.error(f"Invalid LED brightness: {value}")
            return f"Invalid LED brightness: {value}"
        
    def start_monitoring(self) -> None:
        """Start continuous monitoring in background thread"""
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()


    def _initialize_hardware(self) -> None:
        try: 
            self.mcp = EasyMCP2221.Device()
            self.mcp.set_pin_function(gp3="DAC")
            self.mcp.DAC_config(ref="VDD")
            
            self.light = LightSensor(self.mcp)
            self.temp = TempSensor(self.mcp)
        except Exception as e:
            logger.error(f"Error reseting the hardware: {e}")
            self.mcp = None
 
    def _monitor_loop(self) -> None:
        """Continuous monitoring and controling loop"""
        while True:
            try:
                luminosity = self.light.read()
                temperature = self.temp.read()
                
                with self.data_lock:
                    self.data.lux_value = luminosity
                    self.data.temp_value = temperature
                    led_brightness = self.data.led_brightness
                    brightness_changed = self.brightness_changed
                    self.data.timestamp = datetime.now()
                
                if self.dac_on:
                    if brightness_changed:
                        self.mcp.DAC_write(led_brightness, norm=True)
                        self.brightness_changed = False

                    if luminosity > self.data.lux_threshold + self.hysteresis:
                        self.mcp.DAC_write(0, norm=True)
                        self.dac_on = False
                else:
                    if luminosity < self.data.lux_threshold:
                        self.mcp.DAC_write(led_brightness, norm=True)
                        self.dac_on = True
                
            except Exception as e:
                logger.error(f"Error in the sensor monitor loop: {e}")
                self._initialize_hardware()
                time.sleep(3)
            
            finally:
                time.sleep(1)
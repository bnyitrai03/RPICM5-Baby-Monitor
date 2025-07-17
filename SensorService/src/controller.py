import EasyMCP2221
import time
from .light_sensor import LightSensor
from .temp_sensor import TempSensor

LIGHT_THRESHOLD = 100

if __name__=="__main__":
    mcp = EasyMCP2221.Device()
    mcp.set_pin_function(gp3 = "GPIO_OUT")

    light = LightSensor(mcp)
    temp = TempSensor(mcp)
    
    while True:
        try:
            luminosity= light.read()
            temperature = temp.read()
            
            if luminosity < LIGHT_THRESHOLD:
                mcp.GPIO_write(gp3 = True)
            else:
                mcp.GPIO_write(gp3 = False)
                
            # Give the sensor data to the endpoint when requested
            
            time.sleep(1)
        except Exception as e:
            print(e)
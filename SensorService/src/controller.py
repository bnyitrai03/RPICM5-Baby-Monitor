import EasyMCP2221
import time
from .light_sensor import LightSensor
from .temp_sensor import TempSensor

if __name__=="__main__":
    mcp = EasyMCP2221.Device()
    lux = LightSensor(mcp)
    cel = TempSensor(mcp)
    
    while True:
        try:
            print(f"Lux: {lux.read()} | Temp: {cel.read()}")
            time.sleep(1)
        except Exception as e:
            print(e)
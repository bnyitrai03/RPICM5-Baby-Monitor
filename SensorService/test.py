import EasyMCP2221
import time

mcp = EasyMCP2221.Device()
mcp.set_pin_function(gp3="GPIO_OUT")

while(True):
    mcp.GPIO_write(gp3=True)
    time.sleep(0.5)
    mcp.GPIO_write(gp3=False)
    time.sleep(0.5)
    print("Cycle Done!")
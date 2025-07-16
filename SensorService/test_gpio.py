import EasyMCP2221
from time import sleep

mcp = EasyMCP2221.Device()
mcp.set_pin_function(gp3 = "GPIO_OUT")
mcp.GPIO_write(gp3 = True)
while True:
    sleep(0.5)
import time
import machine
import network
from microWebSrv import MicroWebSrv

from LedController import LedController
from Web import Web

ledController = LedController(13, 16)
ledController.all_off()
ledController.pulse_status_led(0, 0, 32)

web = Web(ledController)

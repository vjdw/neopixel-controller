from machine import RTC, Pin
import network
from microWebSrv import MicroWebSrv

from LedController import LedController
from Scheduler import Scheduler
from Web import Web

# Ambilight:
ledController = LedController(13, 16, 3)
# Backlight:
#ledController = LedController(13, 30, 4)

ledController.all_off()
ledController.pulse_status_led(0, 0, 32, 0)

scheduler = Scheduler(ledController)

web = Web(ledController, scheduler)

scheduler.run()

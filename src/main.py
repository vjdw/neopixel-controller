import time
import utime
from ntptime import settime
from machine import RTC, Pin
import network
from microWebSrv import MicroWebSrv

from LedController import LedController
from Web import Web

ledController = LedController(13, 16)
ledController.all_off()
ledController.pulse_status_led(0, 0, 32)

web = Web(ledController)

settime()
scheduled_time = utime.mktime((2019,12,7,21,51,0,0,344))
while True:
    if utime.ticks_diff(scheduled_time, utime.time()) > 0:
        utime.sleep_ms(5000)
    else:
        ledController.fade_to_colour(40,8,2)
        break        

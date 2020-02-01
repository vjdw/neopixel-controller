from machine import RTC, Pin
import network
from microWebSrv import MicroWebSrv
import ujson

import WifiConnect
from LedController import LedController
from Scheduler import Scheduler
from Web import Web

hostname = open("config.hostname.txt").read()
print("hostname = {}".format(hostname))
config_file = "config.{0}.json".format(hostname)
config = ujson.loads(open(config_file).read())
print("config = {}".format(config))

ssid = config.get("ssid")
password = open("wifi-password.txt").read()
WifiConnect.connect(ssid, password, hostname)

led_data_pin = int(config.get("led_data_pin"))
led_count = int(config.get("led_count"))
led_bpp = int(config.get("led_bpp"))
ledController = LedController(led_data_pin, led_count, led_bpp)

ledController.all_off()
ledController.pulse_status_led(0, 12, 32, 0)

scheduler = Scheduler(ledController)

web = Web(ledController, scheduler)

scheduler.run()

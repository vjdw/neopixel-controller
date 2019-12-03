import time
import machine
import neopixel

class LedController:

    def __init__(self, pin, led_count):
        self.R = 0
        self.G = 0
        self.B = 0
        self.leds = neopixel.NeoPixel(machine.Pin(pin), led_count)

    def all_off(self):
        for i in range(self.leds.n):
            self.leds[i] = (0, 0, 0)
        self.leds.write()

    def pulse_status_led(self, r, g, b):
        self.leds[0] = (r, g, b)
        self.leds.write()
        time.sleep(1)
        self.leds[0] = (self.R, self.G, self.B)
        self.leds.write()

    def fade_to_colour(self, r, g, b):
        steps = 100
        deltaR = (r - self.R) / steps
        deltaG = (g - self.G) / steps
        deltaB = (b - self.B) / steps
        for step in range(steps):
            for i in range(self.leds.n):
                self.leds[i] = (int(self.R + (deltaR * step)), int(self.G + (deltaG * step)), int(self.B + (deltaB * step)))
            self.leds.write()
            time.sleep_ms(10)
        self.R = r
        self.G = g
        self.B = b
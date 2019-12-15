import utime
import machine
import neopixel

class LedController:

    def __init__(self, pin, led_count, bpp):
        self.R = 0
        self.G = 0
        self.B = 0
        self.W = 0
        self.leds = neopixel.NeoPixel(machine.Pin(pin), led_count, bpp=bpp)
        self.bpp = bpp

    def all_off(self):
        for i in range(self.leds.n):
            self.leds[i] = (0, 0, 0, 0)
        self.leds.write()

    def pulse_status_led(self, r, g, b, w):
        self.leds[0] = (r, g, b, w)
        self.leds.write()
        utime.sleep_ms(1000)
        self.leds[0] = (self.R, self.G, self.B, self.W)
        self.leds.write()

    def fade_to_colour(self, r, g, b, w):
        steps = 50
        deltaR = (r - self.R) / steps
        deltaG = (g - self.G) / steps
        deltaB = (b - self.B) / steps
        deltaW = (w - self.W) / steps
        for step in range(steps):
            for i in range(self.leds.n):
                self.leds[i] = (int(self.R + (deltaR * step)), int(self.G + (deltaG * step)), int(self.B + (deltaB * step)), int(self.W + (deltaW * step)))
            self.leds.write()
            utime.sleep_ms(25)
        self.R = r
        self.G = g
        self.B = b
        self.W = w

    def increase_red(self, delta):
        self.R += delta
        if self.R > 255:
            self.R = 0
        for i in range(self.leds.n):
            self.leds[i] = (self.R, self.G, self.B)
        self.leds.write()

    def increase_green(self, delta):
        self.G += delta
        if self.G > 255:
            self.G = 0
        for i in range(self.leds.n):
            self.leds[i] = (self.R, self.G, self.B)
        self.leds.write()

    def increase_blue(self, delta):
        self.B += delta
        if self.B > 255:
            self.B = 0
        for i in range(self.leds.n):
            self.leds[i] = (self.R, self.G, self.B)
        self.leds.write()
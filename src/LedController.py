import utime
import machine
import neopixel

class LedController:

    def __init__(self, pin, led_count, bpp):
        if (bpp < 3 or bpp > 4):
            raise Exception('bpp must be 3 or 4')

        self.R = 0
        self.G = 0
        self.B = 0
        self.W = 0
        self.leds = neopixel.NeoPixel(machine.Pin(pin), led_count, bpp=bpp)
        self.bpp = bpp

    def all_off(self):
        for i in range(self.leds.n):
            self.leds[i] = self.make_colour_tuple(0, 0, 0, 0)
        self.leds.write()

    def pulse_status_led(self, r, g, b, w):
        self.leds[0] = self.make_colour_tuple(r, g, b, w)
        self.leds.write()
        utime.sleep_ms(1000)
        self.leds[0] = self.make_colour_tuple(self.R, self.G, self.B, self.W)
        self.leds.write()

    def fade_to_colour(self, r, g, b, w):
        steps = 50
        deltaR = (r - self.R) / steps
        deltaG = (g - self.G) / steps
        deltaB = (b - self.B) / steps
        deltaW = (w - self.W) / steps
        if (deltaR == 0 and deltaG == 0 and deltaB == 0 and deltaW == 0):
            return

        for step in range(steps):
            for i in range(self.leds.n):
                self.leds[i] = self.make_colour_tuple(int(self.R + (deltaR * step)), int(self.G + (deltaG * step)), int(self.B + (deltaB * step)), int(self.W + (deltaW * step)))
            self.leds.write()
            utime.sleep_ms(25)
        self.R = r
        self.G = g
        self.B = b
        self.W = w

    def make_colour_tuple(self, r, g, b, w):
        if self.bpp == 3:
            return (r, g, b)
        return (r, g, b, w)

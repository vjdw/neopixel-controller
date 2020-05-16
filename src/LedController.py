import utime
import machine
import neopixel
import random
from Pixels import Pixels

class LedController:

    def __init__(self, pin, led_count, bpp):
        if (bpp < 3 or bpp > 4):
            raise Exception('bpp must be 3 or 4')

        self.R = 0
        self.G = 0
        self.B = 0
        self.W = 0
        self.Target_R = 0
        self.Target_G = 0
        self.Target_B = 0
        self.Target_W = 0

        self.leds = Pixels(machine.Pin(pin), led_count, 2)
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

    def set_target(self, r, g, b, w):
        self.Target_R = r
        self.Target_G = g
        self.Target_B = b
        self.Target_W = w

    def fade_to_target(self, delta_denominator):
        if delta_denominator < 1:
            delta_denominator = 1

        deltaR = self.calc_fade_colour(self.R, self.Target_R, delta_denominator)
        deltaG = self.calc_fade_colour(self.G, self.Target_G, delta_denominator)
        deltaB = self.calc_fade_colour(self.B, self.Target_B, delta_denominator)
        deltaW = self.calc_fade_colour(self.W, self.Target_W, delta_denominator)

        print("target {}:{}:{} denom: {} delta {}:{}:{}".format(self.Target_R, self.Target_G, self.Target_B, delta_denominator, deltaR, deltaG, deltaB))

        colour_change = (abs(deltaR) + abs(deltaG) + abs(deltaB) + abs(deltaW)) > 0

        if colour_change:
            newR = int(self.R + deltaR)
            newG = int(self.G + deltaG)
            newB = int(self.B + deltaB)
            newW = int(self.W + deltaW)

            slow_mode = delta_denominator > 6
            step_colour = self.make_colour_tuple(newR, newG, newB, newW)
            for i in range(self.leds.n):
                self.leds[i] = step_colour
                self.leds.write()
                utime.sleep_ms(int(max(0, 250 - int(8 * self.leds.n)) / self.leds.n))
                if slow_mode:
                    utime.sleep_ms(int(2400 / self.leds.n))

            self.R = newR
            self.G = newG
            self.B = newB
            self.W = newW

        # True if we weren't at the target colour when this function was called
        return colour_change

    def calc_fade_colour(self, current, target, delta_denominator):
        delta = target - current
        if abs(delta) >= delta_denominator:
            delta = delta / delta_denominator
        elif delta > 0:
            delta = 1
        elif delta < 0:
            delta = -1
        return delta

    def make_colour_tuple(self, r, g, b, w):
        if self.bpp == 3:
            return [g, r, b]
        return [g, r, b, w]
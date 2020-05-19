# Copyright public licence and also I don't care.
# 2020 Josh "NeverCast" Lloyd.
from micropython import const 
#from esp32 import RMT
import esp32

# The peripheral clock is 80MHz or 12.5 nanoseconds per clock.
# The smallest precision of timing requried for neopixels is
# 0.35us, but I've decided to go with 0.05 microseconds or
# 50 nanoseconds. 50 nanoseconds = 12.5 * 4 clocks.
# By dividing the 80MHz clock by 4 we get a clock every 50 nanoseconds.

# Neopixel timing in RMT clock counts.
T_0H = const(35 // 5) # 0.35 microseconds / 50 nanoseconds
T_1H = const(70 // 5) # 0.70 microseconds / 50 nanoseconds
T_0L = const(80 // 5) # 0.80 microseconds / 50 nanoseconds
T_1L = const(60 // 5) # 0.60 microseconds / 50 nanoseconds

# Encoded timings for bits 0 and 1.
D_ZERO = (T_0H, T_0L)
D_ONE = (T_1H, T_1L)

# [D_ONE if ((channel >> bit) & 1) else D_ZERO for channel in channels for bit in range(num_bits - 1, -1, -1)]
# Reset signal is low for longer than 50 microseconds.
T_RST = const(510 // 5) # > 50 microseconds / 50 nanoseconds

# Channel width in bits 
CHANNEL_WIDTH = const(8)

class Pixels:


    def __init__(self, pin, pixel_count, rmt_channel=1, pixel_channels=3):
        self.rmt = esp32.RMT(rmt_channel, pin=pin, clock_div=4)
        # pixels stores the data sent out via RMT
        self.channels = pixel_channels
        single_pixel = (0,) * pixel_channels
        self.pixels = [D_ZERO * (pixel_channels * CHANNEL_WIDTH)] * pixel_count
        # colors is only used for __getitem__
        self.colors = [single_pixel] * pixel_count
        self.n = pixel_count

    def write(self):
        # The bus should be idle low ( I think... )
        # So we finish low and start high.
        pulses = tuple()
        for pixel in self.pixels:
            pulses += pixel
        pulses += (T_RST,) # The last low should be long.
        self.rmt.write_pulses(pulses, start=1)

    def __setitem__(self, pixel_index, colors):
        self_colors = self.colors
        self_pixels = self.pixels 
        if isinstance(pixel_index, int):
            # pixels[0] = (r, g, b)
            self_colors[pixel_index] = tuple(colors)
            self_pixels[pixel_index] = tuple(clocks for bit in (D_ONE if ((channel >> bit) & 1) else D_ZERO for channel in colors for bit in range(CHANNEL_WIDTH - 1, -1, -1)) for clocks in bit)
        elif isinstance(pixel_index, slice):
            start = 0 if pixel_index.start is None else pixel_index.start
            stop = len(self.pixels) if pixel_index.stop is None else pixel_index.stop
            step = 1 if pixel_index.step is None else pixel_index.step
            # Assume that if the first colors element is an int, then its not a sequence
            # Otherwise always assume its a sequence of colors
            if isinstance(colors[0], int):
                # pixels[:] = (r,g,b)
                for index in range(start, stop, step):
                    self_colors[index] = tuple(colors)
                    self_pixels[index] = tuple(clocks for bit in (D_ONE if ((channel >> bit) & 1) else D_ZERO for channel in colors for bit in range(CHANNEL_WIDTH - 1, -1, -1)) for clocks in bit)
            else:
                # pixels[:] = [(r,g,b), ...]
                # Assume its a sequence, make it a list so we know the length
                if not isinstance(colors, list):
                    colors = list(colors)
                color_length = len(colors)
                for index in range(start, stop, step):
                    color = colors[(index - start) % color_length]
                    self_colors[index] = tuple(color)
                    self_pixels[index] = tuple(clocks for bit in (D_ONE if ((channel >> bit) & 1) else D_ZERO for channel in color for bit in range(CHANNEL_WIDTH - 1, -1, -1)) for clocks in bit)
        else:
            raise TypeError('Unsupported pixel_index {} ({})'.format(pixel_index, type(pixel_index)))

    def __getitem__(self, pixel_index):
        # slice instances are passed through
        return self.colors[pixel_index]
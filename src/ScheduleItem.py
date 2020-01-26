import utime

class ScheduleItem:

    def __init__(self, r, g, b, w, dayTicks):
        self.R = r
        self.G = g
        self.B = b
        self.W = w
        self.ticks_past_midnight = dayTicks

    def to_string(self):
        now = utime.localtime()
        midnight_ticks = utime.mktime((now[0], now[1], now[2], 0, 0, 0, 0, 0))
        absolute_ticks = midnight_ticks + self.ticks_past_midnight
        absolute = utime.localtime(absolute_ticks)
        return "R:{0} G:{1} B:{2} W:{3} @ {4}:{5}".format(self.R, self.G, self.B, self.W, absolute[3], absolute[4])
    
    def to_json(self):
        now = utime.localtime()
        midnight_ticks = utime.mktime((now[0], now[1], now[2], 0, 0, 0, 0, 0))
        absolute_ticks = midnight_ticks + self.ticks_past_midnight
        absolute = utime.localtime(absolute_ticks)
        return '{{\"r\":{0}, \"g\":{1}, \"b\":{2}, \"w\":{3}, \"hour\":{4}, \"minute\":{5}, \"ticks\":{6}}}'.format(self.R, self.G, self.B, self.W, absolute[3], absolute[4], self.ticks_past_midnight)

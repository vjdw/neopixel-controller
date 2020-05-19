import time
import machine
import time
import utime
import ujson
import random
from ntptime import settime

from ScheduleItem import ScheduleItem

class Scheduler:

    def __init__(self, ledController):
        self.ledController = ledController

        self.dirty = False
        self.mode = "schedule"
        self.static_colour = (5, 4, 3, 0)

        self.rainbow_brightness = 85
        self.rainbow_hue = 0

        timeset = False
        while not timeset:
            try:
                settime()
                timeset = True
            except Exception:
                print("Exception calling settime, retrying...")
                utime.sleep_ms(5000)

        now = utime.localtime()
        midnight_ticks_today = utime.mktime((now[0], now[1], now[2], 0, 0, 0, 0, 0))
        midnight_ticks_tomorrow = utime.mktime((now[0], now[1], now[2] + 1, 0, 0, 0, 0, 0))
        self.ticks_in_a_day = midnight_ticks_tomorrow - midnight_ticks_today

        self.load_scheduler_config()

    def run(self):
        loop_delay_ms = 250
        loop_counter = 0
        slept_since_set_mode = 0
        since_settime_ms = 0
        fade_steps = 1
        colour_changed = False

        while True:
            loop_counter += 1
            if loop_counter > 255:
                loop_counter = 0

            self.dirty = self.dirty or ((self.mode == "schedule" or self.mode == "random") and slept_since_set_mode > 16000)
            if self.dirty:
                self.dirty = False
                print('dirty mode={} slept_since_set_mode={}'.format(self.mode, slept_since_set_mode))
                if self.mode == "schedule":
                    self.apply_scheduled_colour()
                    slept_since_set_mode = 0
                elif self.mode == "on":
                    self.ledController.set_target(self.static_colour[0], self.static_colour[1], self.static_colour[2], self.static_colour[3])
                elif self.mode == "random":
                    self.apply_rainbow_colour()
                    slept_since_set_mode = 0
                elif self.mode == "off":
                    self.ledController.set_target(0, 0, 0, 0)

            if self.mode == "random":
                if loop_counter % 5 == 0:
                    fade_steps = int(self.rainbow_brightness / 8)
                    colour_changed = self.ledController.fade_to_target(fade_steps)
                else:
                    colour_changed = False
            elif self.mode == "schedule":
                if loop_counter % 8 == 0:
                    fade_steps = 4
                    colour_changed = self.ledController.fade_to_target(fade_steps)
                else:
                    colour_changed = False
            else:
                fade_steps = 1.414
                colour_changed = self.ledController.fade_to_target(fade_steps)

            if not colour_changed:
                utime.sleep_ms(loop_delay_ms)
            slept_since_set_mode += loop_delay_ms
            since_settime_ms += loop_delay_ms

            if since_settime_ms > 86400000: # 24 hours
                try:
                    settime()
                    since_settime_ms = 0
                except Exception:
                    print("Exception calling settime")
                    since_settime_ms = 82800000 # retry in 1 hour
                
    def apply_scheduled_colour(self):
        if len(self.schedule) == 0:
            self.ledController.set_target(0, 0, 0, 0)
            return

        now = utime.localtime()
        now_ticks = utime.mktime(now)
        midnight_ticks = utime.mktime((now[0], now[1], now[2], 0, 0, 0, 0, 0))
        now_ticks_past_midnight = now_ticks - midnight_ticks

        schedule_next = None

        sorted_keys = sorted(self.schedule.keys())

        for i, schedule_key in enumerate(sorted_keys):
            schedule_item = self.schedule[schedule_key]
            if schedule_item.ticks_past_midnight > now_ticks_past_midnight:
                print("{0} <<<".format(schedule_item.to_string()))
                schedule_next = self.schedule[sorted_keys[i]]
                schedule_previous = self.schedule[sorted_keys[i-1]]
                break
            else:
                print("{0}".format(schedule_item.to_string()))
        if schedule_next is None:
            schedule_next = self.schedule[sorted_keys[0]]
            schedule_previous = self.schedule[sorted_keys[-1]]
            print("{0} <<<".format(schedule_next.to_string()))

        ticks_past_previous_schedule = now_ticks_past_midnight - schedule_previous.ticks_past_midnight
        print(str(ticks_past_previous_schedule) + ' ticks past ' + schedule_previous.to_string())

        new_r = self.interpolate_colour(schedule_previous, schedule_next, now_ticks_past_midnight, 'R')
        new_g = self.interpolate_colour(schedule_previous, schedule_next, now_ticks_past_midnight, 'G')
        new_b = self.interpolate_colour(schedule_previous, schedule_next, now_ticks_past_midnight, 'B')
        new_w = self.interpolate_colour(schedule_previous, schedule_next, now_ticks_past_midnight, 'W')
        self.ledController.set_target(new_r, new_g, new_b, new_w)

    def apply_rainbow_colour(self):
        if self.rainbow_brightness > 85:
            self.rainbow_brightness = 85

        # limit to reddish hues
        self.rainbow_hue = random.randint(0, 160)
        if self.rainbow_hue > 70:
            self.rainbow_hue += 199

        h = self.rainbow_hue
        s = 1.0
        l = 0.5

        # hsl -> rgb
        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = l - c/2
        if 0 <= h and h < 60:
            r = c + m
            g = x + m
            b = m
        elif 60 <= h and h < 120:
            r = x + m
            g = c + m
            b = m
        elif 120 <= h and h < 180:
            r = m
            g = c + m
            b = x + m
        elif 180 <= h and h < 240:
            r = m
            g = x + m
            b = c + m
        elif 240 <= h and h < 300:
            r = x + m
            g = m
            b = c + m
        elif 300 <= h and h < 360:
            r = c + m
            g = m
            b = x + m

        r *= self.rainbow_brightness
        g *= self.rainbow_brightness
        b *= self.rainbow_brightness

        self.ledController.set_target(int(r), int(g), int(b), 0)

    def set_mode(self, mode):
        if mode == 'on' or mode == 'off' or mode == 'schedule' or mode == 'random':
            self.mode = mode
            self.dirty = True
            return

        raise Exception('Invalid mode: ' + mode)

    def set_static_colour(self, r, g, b, w):
        self.static_colour = (r, g, b, w)
        self.dirty = True

    def set_rainbow_brightness(self, brightness):
        self.rainbow_brightness = brightness
        self.dirty = True

    def add_schedule_item(self, r, g, b, w, hour, minute):
        now = utime.localtime()
        midnight_ticks = utime.mktime((now[0], now[1], now[2], 0, 0, 0, 0, 0))
        new_schedule_ticks = utime.mktime((now[0], now[1], now[2], hour, minute, 0, 0, 0))
        new_schedule_ticks_past_midnight = new_schedule_ticks - midnight_ticks
        self.schedule[new_schedule_ticks_past_midnight] = ScheduleItem(r, g, b, w, new_schedule_ticks_past_midnight)
        self.save_scheduler_config()
        self.dirty = True

    def delete_schedule_item(self, hour, minute):
        now = utime.localtime()
        midnight_ticks = utime.mktime((now[0], now[1], now[2], 0, 0, 0, 0, 0))
        new_schedule_ticks = utime.mktime((now[0], now[1], now[2], hour, minute, 0, 0, 0))
        new_schedule_ticks_past_midnight = new_schedule_ticks - midnight_ticks
        del self.schedule[new_schedule_ticks_past_midnight]
        self.save_scheduler_config()
        self.dirty = True

    def interpolate_colour(self, schedulePrevious, scheduleNext, ticks_past_midnight_now, colour):
        nextTicks = scheduleNext.ticks_past_midnight
        prevTicks = schedulePrevious.ticks_past_midnight
        nowTicks = ticks_past_midnight_now

        if prevTicks > nowTicks:
            prevTicks -= self.ticks_in_a_day
        if nextTicks < nowTicks:
            nextTicks += self.ticks_in_a_day

        ticks_past_previous_schedule = nowTicks - prevTicks
        prev_next_diff_ticks = nextTicks - prevTicks
        if prev_next_diff_ticks > 0:
            return getattr(schedulePrevious, colour) + round((ticks_past_previous_schedule / prev_next_diff_ticks) * (getattr(scheduleNext, colour) - getattr(schedulePrevious, colour)))
        else:
            return getattr(schedulePrevious, colour)

    def to_json(self):
        sorted_keys = sorted(self.schedule.keys())
        schedule_json = '[{}]'.format(', '.join(self.schedule[x].to_json() for x in sorted_keys))
        return '{{\"mode\":\"{}\", \"staticColour\":\"{}\", \"schedule\":{}}}'.format(self.mode, self.static_colour, schedule_json)

    def to_json_schedule_as_dict(self):
        sorted_keys = sorted(self.schedule.keys())
        schedule_json = '{{{}}}'.format(', '.join('{}: {}'.format(x, self.schedule[x].to_json()) for x in sorted_keys))
        return '{{\"mode\":\"{}\", \"staticColour\":\"{}\", \"schedule\":{}}}'.format(self.mode, self.static_colour, schedule_json)

    def save_scheduler_config(self):
        config_file = open("scheduler.json", "w")
        config_file.write(self.to_json_schedule_as_dict())
        config_file.close()

    def load_scheduler_config(self):
        config = ujson.loads(open("scheduler.json").read())
        self.mode = config["mode"]
        self.static_colour = tuple(map(int, config["staticColour"].replace("(", "").replace(")", "").replace(" ", "").split(",")))

        schedule = config["schedule"]
        self.schedule = dict((key, ScheduleItem(schedule[key]['r'], schedule[key]['g'], schedule[key]['b'], schedule[key]['w'], key)) for key in schedule)

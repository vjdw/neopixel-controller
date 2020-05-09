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

        self.rainbow_brightness = 16
        self.rainbow_brightness_allocation = [2, 0, 0]

        settime()

        now = utime.localtime()
        midnight_ticks_today = utime.mktime((now[0], now[1], now[2], 0, 0, 0, 0, 0))
        midnight_ticks_tomorrow = utime.mktime((now[0], now[1], now[2] + 1, 0, 0, 0, 0, 0))
        self.ticks_in_a_day = midnight_ticks_tomorrow - midnight_ticks_today

        self.load_scheduler_config()

    def run(self):
        loop_delay_ms = 250
        slept_since_set_mode = 0

        while True:
            self.dirty = self.dirty or (self.mode in ("schedule", "random") and slept_since_set_mode > 8000)
            if self.dirty:
                if self.mode == "schedule":
                    slept_since_set_mode = 0
                    self.apply_scheduled_colour()
                elif self.mode == "on":
                    slept_since_set_mode = 0
                    self.ledController.fade_to_colour(self.static_colour[0], self.static_colour[1], self.static_colour[2], self.static_colour[3])
                elif self.mode == "random":
                    slept_since_set_mode = 0
                    self.apply_rainbow_colour()
                elif self.mode == "off":
                    slept_since_set_mode = 0
                    self.ledController.fade_to_colour(0, 0, 0, 0)
                self.dirty = False

            utime.sleep_ms(loop_delay_ms)
            slept_since_set_mode += loop_delay_ms
            if slept_since_set_mode > 86400000: # 24 hours
                try:
                    settime()
                except Exception:
                    print("Exception calling settime")
                slept_since_set_mode = 0

    def apply_scheduled_colour(self):
        if len(self.schedule) == 0:
            self.ledController.fade_to_colour(0, 0, 0, 0)
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
        self.ledController.fade_to_colour(new_r, new_g, new_b, new_w)

    def apply_rainbow_colour(self):
        if self.rainbow_brightness > 85:
            self.rainbow_brightness = 85

        allocation_to_move = random.randint(0, 2)
        while self.rainbow_brightness_allocation[allocation_to_move] == 0:
            allocation_to_move = random.randint(0, 2)

        # take a unit away...
        self.rainbow_brightness_allocation[allocation_to_move] = self.rainbow_brightness_allocation[allocation_to_move] - 1

        # ...and randomly add it to a neighbour
        if random.randint(0, 1) == 0:
            direction = 1
        else:
            direction = -1
        allocation_to_move = allocation_to_move + direction
        if allocation_to_move >= len(self.rainbow_brightness_allocation):
            allocation_to_move = 0
        self.rainbow_brightness_allocation[allocation_to_move] = self.rainbow_brightness_allocation[allocation_to_move] + 1

        # Prevent pure white (undo allocation and move allocation to the next neighbour)
        if 0 not in self.rainbow_brightness_allocation:
            self.rainbow_brightness_allocation[allocation_to_move] = self.rainbow_brightness_allocation[allocation_to_move] - 1
            allocation_to_move = allocation_to_move + direction
            if allocation_to_move >= len(self.rainbow_brightness_allocation):
                allocation_to_move = 0
            self.rainbow_brightness_allocation[allocation_to_move] = self.rainbow_brightness_allocation[allocation_to_move] + 1

        r = (1 + self.rainbow_brightness_allocation[0]) * self.rainbow_brightness
        g = self.rainbow_brightness_allocation[1] * self.rainbow_brightness
        b = self.rainbow_brightness_allocation[2] * self.rainbow_brightness
        self.ledController.fade_to_colour_slow(r, g, b, 0)

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

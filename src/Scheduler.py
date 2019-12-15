import time
import machine
import time
import utime
from ntptime import settime

from ScheduleItem import ScheduleItem

class Scheduler:

    def __init__(self, ledController):
        self.ledController = ledController

        settime()

        now = utime.localtime()
        midnight_ticks_today = utime.mktime((now[0], now[1], now[2], 0, 0, 0, 0, 0))
        midnight_ticks_tomorrow = utime.mktime((now[0], now[1], now[2] + 1, 0, 0, 0, 0, 0))
        self.ticks_in_a_day = midnight_ticks_tomorrow - midnight_ticks_today

        self.schedule = [
                ScheduleItem(0, 0, 0, 0, utime.mktime((now[0], now[1], now[2], 5, 50, 0, 0, 0)) - midnight_ticks_today),
                ScheduleItem(16, 4, 1, 0, utime.mktime((now[0], now[1], now[2], 6, 0, 0, 0, 0)) - midnight_ticks_today),
                ScheduleItem(32, 8, 2, 0, utime.mktime((now[0], now[1], now[2], 6, 40, 0, 0, 0)) - midnight_ticks_today),
                ScheduleItem(0, 0, 0, 0, utime.mktime((now[0], now[1], now[2], 6, 41, 0, 0, 0)) - midnight_ticks_today),
                ScheduleItem(0, 0, 0, 0, utime.mktime((now[0], now[1], now[2], 15, 59, 0, 0, 0)) - midnight_ticks_today),
                ScheduleItem(48, 12, 3, 0, utime.mktime((now[0], now[1], now[2], 16, 0, 0, 0, 0)) - midnight_ticks_today),
                ScheduleItem(32, 8, 2, 0, utime.mktime((now[0], now[1], now[2], 21, 0, 0, 0, 0)) - midnight_ticks_today),
                ScheduleItem(16, 4, 1, 0, utime.mktime((now[0], now[1], now[2], 23, 58, 0, 0, 0)) - midnight_ticks_today),
                ScheduleItem(0, 0, 0, 0, utime.mktime((now[0], now[1], now[2], 23, 59, 0, 0, 0)) - midnight_ticks_today)
            ]
        self.schedule.sort(key=lambda x:x.ticks_past_midnight)

    def run(self):
        while True:
            now = utime.localtime()
            now_ticks = utime.mktime(now)
            midnight_ticks = utime.mktime((now[0], now[1], now[2], 0, 0, 0, 0, 0))
            now_ticks_past_midnight = now_ticks - midnight_ticks

            schedule_next = None
            for i, schedule_enum in enumerate(self.schedule):
                if schedule_enum.ticks_past_midnight > now_ticks_past_midnight:
                    print("{0} <<<".format(schedule_enum.to_string()))
                    schedule_next = self.schedule[i]
                    schedule_previous = self.schedule[i-1]
                    break
                else:
                    print("{0}".format(schedule_enum.to_string()))
            if schedule_next is None:
                schedule_next = self.schedule[0]
                schedule_previous = self.schedule[-1]
                print("{0} <<<".format(schedule_next.to_string()))

            ticks_past_previous_schedule = now_ticks_past_midnight - schedule_previous.ticks_past_midnight
            print(str(ticks_past_previous_schedule) + ' ticks past ' + schedule_previous.to_string())

            new_r = self.interpolate_colour(schedule_previous, schedule_next, now_ticks_past_midnight, 'R')
            new_g = self.interpolate_colour(schedule_previous, schedule_next, now_ticks_past_midnight, 'G')
            new_b = self.interpolate_colour(schedule_previous, schedule_next, now_ticks_past_midnight, 'B')
            new_w = self.interpolate_colour(schedule_previous, schedule_next, now_ticks_past_midnight, 'W')
            self.ledController.fade_to_colour(new_r, new_g, new_b, new_w)
            utime.sleep_ms(5000)

    def add_schedule_item(self, r, g, b, w, hour, minute):
        now = utime.localtime()
        midnight_ticks = utime.mktime((now[0], now[1], now[2], 0, 0, 0, 0, 0))
        new_schedule_ticks = utime.mktime((now[0], now[1], now[2], hour, minute, 0, 0, 0))
        new_schedule_ticks_past_midnight = new_schedule_ticks - midnight_ticks

        self.schedule.append(ScheduleItem(r, g, b, w, new_schedule_ticks_past_midnight))
        self.schedule.sort(key=lambda x:x.ticks_past_midnight)

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

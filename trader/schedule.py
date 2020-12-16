import datetime
import schedule
from typing import List


class TraderController:

    ORCHESTRATION_TIME = '20:30'

    def __init__(self,
                 start_time: str,
                 end_time: str):

        self._start_time = start_time
        self._end_time = end_time

    def get_action(self):
        pass


class ScheduleHelper:

    day_map = {'Sunday': 1, 'Monday': 2, 'Tuesday': 3, 'Wednesday': 4, 'Thursday': 5, 'Friday': 6, 'Saturday': 7}
    freq_map = {'m1': 1, 'm5': 5}

    START_TIME = '06:59'
    END_TIME = '19:59'
    END_TIME_FRI = '19:59'

    ORCHESTRATION_TIME = '20:30'

    def __init__(self, time_now, frequency):

        if frequency not in list(self.freq_map.keys()):
            raise AttributeError(f'Frequency {frequency} not supported.')

        self._time_now = time_now
        self._frequency = frequency

    def get_schedule(self, day: str):
        if day == 'Friday':
            end_time = self.END_TIME_FRI
        else:
            end_time = self.END_TIME

        if self.week_number_now < ScheduleHelper.day_map[day]:
            return []

        elif self.week_number_now == ScheduleHelper.day_map[day]:
            next_time = self._time_now - datetime.timedelta(minutes=(self._time_now.minute % self.freq_map[self._frequency]),
                                                            seconds=self._time_now.second,
                                                            microseconds=self._time_now.microsecond)
            next_time += datetime.timedelta(minutes=self.freq_map[self._frequency])
            return self.get_time_intervals(next_time.strftime('%H:%M'), end_time)

        else:
            return []

    def get_time_intervals(self, start: str, end: str) -> List[str]:
        all_times = []

        allowed_start_time = datetime.datetime.strptime(self.START_TIME, "%H:%M")

        start = datetime.datetime.strptime(start, "%H:%M")
        end = datetime.datetime.strptime(end, "%H:%M")

        t = start

        while t <= end:
            if allowed_start_time < t:
                all_times.append(t.strftime("%H:%M"))
            t += datetime.timedelta(minutes=self.freq_map[self._frequency])

        return all_times

    @property
    def monday(self) -> List[str]:
        return self.get_schedule('Monday')

    @property
    def tuesday(self) -> List[str]:
        return self.get_schedule('Tuesday')

    @property
    def wednesday(self) -> List[str]:
        return self.get_schedule('Wednesday')

    @property
    def thursday(self) -> List[str]:
        return self.get_schedule('Thursday')

    @property
    def friday(self) -> List[str]:
        return self.get_schedule('Friday')

    @property
    def week_number_now(self) -> int:
        return ScheduleHelper.day_map[self._time_now.strftime('%A')]


def initialize_schedule(_trader, frequency) -> None:

    now = datetime.datetime.utcnow()

    helper = ScheduleHelper(time_now=now, frequency=frequency)

    for monday_time in helper.monday:
        schedule.every().monday.at(monday_time).do(_trader.process_timestep)

    for tuesday_time in helper.tuesday:
        schedule.every().tuesday.at(tuesday_time).do(_trader.process_timestep)

    for wednesday_time in helper.wednesday:
        schedule.every().wednesday.at(wednesday_time).do(_trader.process_timestep)

    for thursday_time in helper.thursday:
        schedule.every().thursday.at(thursday_time).do(_trader.process_timestep)

    for friday_time in helper.friday:
        schedule.every().friday.at(friday_time).do(_trader.process_timestep)

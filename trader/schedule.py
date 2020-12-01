import datetime
from typing import List


class ScheduleHelper:

    day_map = {'Sunday': 1, 'Monday': 2, 'Tuesday': 3, 'Wednesday': 4, 'Thursday': 5, 'Friday': 6, 'Saturday': 7}

    def __init__(self, time_now, frequency):

        self._time_now = time_now
        self._frequency = frequency

    def get_schedule(self, day: str):
        if day == 'Friday':
            end_time = '20:55'
        else:
            end_time = '23:55'

        if self.week_number_now < ScheduleHelper.day_map[day]:
            return self.get_time_intervals('00:00', end_time)
        elif self.week_number_now == ScheduleHelper.day_map[day]:
            next_time = self._time_now - datetime.timedelta(minutes=(self._time_now.minute % 5),
                                                            seconds=self._time_now.second,
                                                            microseconds=self._time_now.microsecond)
            next_time += datetime.timedelta(minutes=5)
            return self.get_time_intervals(next_time.strftime('%H:%M'), end_time)

        else:
            return []

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

    @property
    def last_run_time(self) -> datetime:
        raise NotImplementedError

    @staticmethod
    def get_time_intervals(start: str, end: str) -> List[str]:
        all_times = []

        start = datetime.datetime.strptime(start, "%H:%M")
        end = datetime.datetime.strptime(end, "%H:%M")

        t = start

        while t <= end:
            all_times.append(t.strftime("%H:%M"))
            t += datetime.timedelta(minutes=5)

        return all_times

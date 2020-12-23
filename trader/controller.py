from datetime import datetime, timedelta
from collections import deque


class TraderController:

    FREQ_MAP = {'m1': 1, 'm5': 5}

    def __init__(self,
                 frequency: str,
                 start_time: str,
                 end_time: str):

        self._frequency = frequency
        self._start_time = datetime.strptime(start_time, '%H:%M')
        self._end_time = datetime.strptime(end_time, '%H:%M')

        self._events = self.get_event_queue()

    def get_action(self) -> str:

        time_now = datetime.utcnow()

        if self.completed:
            return 'shutdown'

        next_decision_time = self._events[0]

        if next_decision_time < time_now:
            _ = self._events.popleft()
            return 'trade'
        else:
            return 'update'

    def get_event_queue(self):

        event_queue = deque()

        start_hour = self._start_time.hour
        end_hour = self._end_time.hour

        now_time = datetime.utcnow()
        now_hour = now_time.hour

        if start_hour < end_hour:
            if now_hour > end_hour or now_hour < start_hour:
                return event_queue
        elif start_hour > end_hour:
            if end_hour < now_hour < start_hour:
                return event_queue
        else:
            raise NotImplementedError

        next_time = now_time - timedelta(
            minutes=(now_time.minute % self.FREQ_MAP[self._frequency]),
            seconds=now_time.second,
            microseconds=now_time.microsecond) + timedelta(minutes=self.FREQ_MAP[self._frequency])

        while next_time.hour != end_hour:
            event_queue.append(next_time)
            next_time += timedelta(minutes=self.FREQ_MAP[self._frequency])

        return event_queue

    @property
    def completed(self):
        return True if len(self._events) == 0 else False

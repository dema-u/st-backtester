import trader
from trader.schedule import ScheduleHelper, TraderController
from datetime import datetime
from unittest.mock import Mock, patch


@patch.object(trader.schedule, 'datetime', Mock(wraps=datetime))
def test_day_controller():
    trader.schedule.datetime.utcnow.return_value = datetime(2020, 1, 1, 7, 34, 5)
    trade_controller = TraderController('m5', '07:00', '20:00')
    print(trade_controller._events)


@patch.object(trader.schedule, 'datetime', Mock(wraps=datetime))
def test_night_controller():
    trader.schedule.datetime.utcnow.return_value = datetime(2020, 1, 1, 22, 34, 5)
    trade_controller = TraderController('m5', '22:00', '06:00')
    print(trade_controller._events)


def test_sunday():
    dt = datetime(2020, 11, 29, 11, 23, 4)
    freq = 'm5'

    helper = ScheduleHelper(dt, freq)

    assert helper.monday == []
    assert helper.tuesday == []
    assert helper.wednesday == []
    assert helper.thursday == []
    assert helper.friday == []


def test_monday_5m():
    dt = datetime(2020, 11, 30, 11, 23, 4)
    freq = 'm5'

    helper = ScheduleHelper(dt, freq)

    assert helper.monday[0] == '11:25'
    assert helper.monday[-1] == '19:55'


def test_monday_1m():
    dt = datetime(2020, 11, 30, 17, 23, 0)
    freq = 'm1'

    helper = ScheduleHelper(dt, freq)

    assert helper.monday[0] == '17:24'
    assert helper.monday[-1] == helper.END_TIME
    assert helper.tuesday == []


def test_tuesday_5m():
    dt = datetime(2020, 12, 1, 11, 23, 4)
    freq = 'm5'

    helper = ScheduleHelper(dt, freq)

    assert helper.monday == []
    assert helper.tuesday[0] == '11:25'
    assert helper.tuesday[-1] == '19:55'
    assert helper.wednesday == []


def test_tuesday_1m():
    dt = datetime(2020, 12, 1, 4, 52, 32)
    freq = 'm1'

    helper = ScheduleHelper(dt, freq)

    assert helper.tuesday[0] == '07:00'
    assert helper.tuesday[-1] == helper.END_TIME
    assert helper.monday == []
    assert helper.friday == []


def test_friday_5m():
    dt = datetime(2020, 12, 4, 15, 1, 4)
    freq = 'm5'

    helper = ScheduleHelper(dt, freq)

    assert helper.thursday == []
    assert helper.friday[0] == '15:05'
    assert helper.friday[-1] == '19:55'


def test_friday_1m():
    dt = datetime(2020, 12, 4, 5, 57, 1)
    freq = 'm1'

    helper = ScheduleHelper(dt, freq)

    assert helper.monday == []
    assert helper.tuesday == []
    assert helper.wednesday == []
    assert helper.thursday == []
    assert helper.friday[0] == '07:00'
    assert helper.friday[-1] == helper.END_TIME_FRI

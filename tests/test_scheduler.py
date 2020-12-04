from trader import ScheduleHelper
from datetime import datetime


def test_monday_5m():
    dt = datetime(2020, 11, 30, 11, 23, 4)
    freq = 'm5'

    helper = ScheduleHelper(dt, freq)

    assert helper.monday[0] == '11:25'
    assert helper.monday[-1] == '23:55'


def test_monday_1m():
    dt = datetime(2020, 11, 30, 23, 23, 0)
    freq = 'm1'

    helper = ScheduleHelper(dt, freq)

    assert helper.monday[0] == '23:24'
    assert helper.monday[-1] == '23:59'


def test_tuesday_5m():
    dt = datetime(2020, 12, 1, 11, 23, 4)
    freq = 'm5'

    helper = ScheduleHelper(dt, freq)

    assert helper.monday == []
    assert helper.tuesday[0] == '11:25'
    assert helper.tuesday[-1] == '23:55'


def test_tuesday_1m():
    dt = datetime(2020, 12, 1, 21, 52, 32)
    freq = 'm1'

    helper = ScheduleHelper(dt, freq)

    assert helper.monday == []
    assert helper.tuesday[0] == '21:53'
    assert helper.tuesday[-1] == '23:59'
    assert helper.friday[0] == '00:00'


def test_friday_5m():
    dt = datetime(2020, 12, 4, 15, 1, 4)
    freq = 'm5'

    helper = ScheduleHelper(dt, freq)

    assert helper.thursday == []
    assert helper.friday[0] == '15:05'
    assert helper.friday[-1] == '19:55'


def test_friday_1m():
    dt = datetime(2020, 12, 4, 19, 57, 1)
    freq = 'm1'

    helper = ScheduleHelper(dt, freq)

    assert helper.monday == []
    assert helper.tuesday == []
    assert helper.wednesday == []
    assert helper.thursday == []
    assert helper.friday[0] == '19:58'
    assert helper.friday[-1] == '19:59'

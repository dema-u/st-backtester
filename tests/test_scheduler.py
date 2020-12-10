from trader.schedule import ScheduleHelper
from datetime import datetime


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
    assert helper.monday[-1] == '17:55'


def test_monday_1m():
    dt = datetime(2020, 11, 30, 17, 23, 0)
    freq = 'm1'

    helper = ScheduleHelper(dt, freq)

    assert helper.monday[0] == '17:24'
    assert helper.monday[-1] == '17:59'
    assert helper.tuesday == []


def test_tuesday_5m():
    dt = datetime(2020, 12, 1, 11, 23, 4)
    freq = 'm5'

    helper = ScheduleHelper(dt, freq)

    assert helper.monday == []
    assert helper.tuesday[0] == '11:25'
    assert helper.tuesday[-1] == '17:55'
    assert helper.wednesday == []


def test_tuesday_1m():
    dt = datetime(2020, 12, 1, 4, 52, 32)
    freq = 'm1'

    helper = ScheduleHelper(dt, freq)

    assert helper.tuesday[0] == '06:00'
    assert helper.tuesday[-1] == '17:59'
    assert helper.monday == []
    assert helper.friday == []


def test_friday_5m():
    dt = datetime(2020, 12, 4, 15, 1, 4)
    freq = 'm5'

    helper = ScheduleHelper(dt, freq)

    assert helper.thursday == []
    assert helper.friday[0] == '15:05'
    assert helper.friday[-1] == '17:55'


def test_friday_1m():
    dt = datetime(2020, 12, 4, 5, 57, 1)
    freq = 'm1'

    helper = ScheduleHelper(dt, freq)

    assert helper.monday == []
    assert helper.tuesday == []
    assert helper.wednesday == []
    assert helper.thursday == []
    assert helper.friday[0] == '06:00'
    assert helper.friday[-1] == '17:59'

import trader
from trader.schedule import TraderController
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


@patch.object(trader.schedule, 'datetime', Mock(wraps=datetime))
def test_day_controller():
    trader.schedule.datetime.utcnow.return_value = datetime(2020, 1, 1, 7, 34, 5)
    trader_controller = TraderController('m5', '07:00', '20:00')

    assert trader_controller._events[0] == datetime(2020, 1, 1, 7, 35, 0, 0)
    assert trader_controller._events[1] == datetime(2020, 1, 1, 7, 40, 0, 0)
    assert trader_controller._events[2] == datetime(2020, 1, 1, 7, 45, 0, 0)
    assert trader_controller._events[-1] == datetime(2020, 1, 1, 19, 55, 0, 0)


@patch.object(trader.schedule, 'datetime', Mock(wraps=datetime))
def test_night_controller():
    trader.schedule.datetime.utcnow.return_value = datetime(2020, 1, 1, 22, 34, 5)
    trader_controller = TraderController('m1', '22:00', '06:00')

    assert trader_controller._events[0] == datetime(2020, 1, 1, 22, 35, 0, 0)
    assert trader_controller._events[1] == datetime(2020, 1, 1, 22, 36, 0, 0)
    assert trader_controller._events[2] == datetime(2020, 1, 1, 22, 37, 0, 0)
    assert trader_controller._events[-1] == datetime(2020, 1, 2, 5, 59, 0, 0)


@patch.object(trader.schedule, 'datetime', Mock(wraps=datetime))
def test_action_controller():
    trader.schedule.datetime.utcnow.return_value = datetime(2020, 1, 1, 7, 34, 5)
    trader_controller = TraderController('m5', '07:00', '20:00')
    time = datetime(2020, 1, 1, 7, 34, 8)

    for _ in range(1000000):
        trader.schedule.datetime.utcnow.return_value = time
        action = trader_controller.get_action()
        time += timedelta(minutes=1)

        if action == 'shutdown':
            break

    assert time == datetime(2020, 1, 1, 19, 57, 8)
    assert action == 'shutdown'


@patch.object(trader.schedule, 'datetime', Mock(wraps=datetime))
def test_completion_controller():
    trader.schedule.datetime.utcnow.return_value = datetime(2020, 1, 1, 22, 34, 5)
    trader_controller = TraderController('m1', '22:00', '06:00')

    trader.schedule.datetime.utcnow.return_value = datetime(2020, 1, 1, 22, 34, 5)

    action = trader_controller.get_action()
    assert action == 'update'

    trader.schedule.datetime.utcnow.return_value = datetime(2020, 1, 1, 22, 35, 5)

    action = trader_controller.get_action()
    assert action == 'trade'

    trader.schedule.datetime.utcnow.return_value = datetime(2020, 1, 1, 22, 36, 5)

    action = trader_controller.get_action()
    assert action == 'trade'

    trader.schedule.datetime.utcnow.return_value = datetime(2020, 1, 1, 22, 36, 10)

    action = trader_controller.get_action()
    assert action == 'update'


@patch.object(trader.schedule, 'datetime', Mock(wraps=datetime))
def test_outside_time_day_controller():
    trader.schedule.datetime.utcnow.return_value = datetime(2020, 1, 1, 21, 34, 5)
    trader_controller = TraderController('m1', '22:00', '06:00')

    assert trader_controller.get_action() == 'shutdown'

    trader.schedule.datetime.utcnow.return_value = datetime(2020, 1, 1, 7, 34, 5)
    trader_controller = TraderController('m1', '22:00', '06:00')

    assert trader_controller.get_action() == 'shutdown'


@patch.object(trader.schedule, 'datetime', Mock(wraps=datetime))
def test_outside_time_night_controller():
    trader.schedule.datetime.utcnow.return_value = datetime(2020, 1, 1, 21, 34, 5)
    trader_controller = TraderController('m5', '07:00', '20:00')

    assert trader_controller.get_action() == 'shutdown'

    trader.schedule.datetime.utcnow.return_value = datetime(2020, 1, 1, 6, 34, 5)
    trader_controller = TraderController('m5', '07:00', '20:00')

    assert trader_controller.get_action() == 'shutdown'

import os
import pytest
import pandas as pd
from backtester.backtester import Broker


@pytest.fixture
def broker():
    file_path = os.path.abspath('test_data/EURUSD-SAMPLE.csv')
    data = pd.read_csv(file_path, index_col=0, parse_dates=True)
    return Broker(data)


def test_market_order_insertion(broker):
    broker.open_market_order(is_long=True,
                             tp=1.0,
                             sl=0.1,
                             size=1)

    orders = broker.orders
    order = orders[0]

    assert len(broker.orders) == 1

    assert order.tp == 1.0
    assert order.sl == 0.1
    assert order._size == 1


def test_entry_order_insertion(broker):
    broker.open_entry_order(is_long=True,
                            limit=None,
                            stop=0.3,
                            tp=1.0,
                            sl=0.1,
                            size=1)

    orders = broker.orders
    order = orders[0]

    assert len(broker.orders) == 1

    assert order.limit is None
    assert order.stop == 0.3
    assert order.tp == 1.0
    assert order.sl == 0.1
    assert order._size == 1


def test_entry_order_cancellation(broker):
    broker.open_entry_order(is_long=True,
                            limit=None,
                            stop=0.3,
                            tp=1.0,
                            sl=0.1,
                            size=1)

    orders = broker.orders
    order = orders[0]
    order.cancel()

    assert len(broker.orders) == 0

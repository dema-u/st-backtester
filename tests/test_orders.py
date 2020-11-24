import pytest
import pandas as pd
from backtester import Broker


@pytest.fixture
def empty_broker():
    return Broker(pd.DataFrame())


def test_market_order_insertion(empty_broker):
    empty_broker.open_market_order(is_long=True,
                                   tp=1.0,
                                   sl=0.1,
                                   size=1)

    orders = empty_broker.orders
    order = orders[0]

    assert len(empty_broker.orders) == 1

    assert order.tp == 1.0
    assert order.sl == 0.1
    assert order._size == 1


def test_entry_order_insertion(empty_broker):
    empty_broker.open_entry_order(is_long=True,
                                  limit=0.2,
                                  stop=0.3,
                                  tp=1.0,
                                  sl=0.1,
                                  size=1)

    orders = empty_broker.orders
    order = orders[0]

    assert len(empty_broker.orders) == 1

    assert order.limit == 0.2
    assert order.stop == 0.3
    assert order.tp == 1.0
    assert order.sl == 0.1
    assert order._size == 1


def test_entry_order_cancellation(empty_broker):
    empty_broker.open_entry_order(is_long=True,
                                  limit=0.2,
                                  stop=0.3,
                                  tp=1.0,
                                  sl=0.1,
                                  size=1)

    orders = empty_broker.orders
    order = orders[0]
    order.cancel()

    assert len(empty_broker.open_orders) == 0

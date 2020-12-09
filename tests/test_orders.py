from unittest.mock import Mock
from trader import Order
import pytest


def test_order_init(simple_order):

    is_long = True
    entry = 1.0
    tp = 2.0
    sl = 0.5
    size = 5
    back_price = 1.5

    assert simple_order.is_long == is_long
    assert simple_order.size == size
    assert simple_order.entry == entry
    assert simple_order.tp == tp
    assert simple_order.sl == sl
    assert simple_order.back_price == back_price


def test_fxcm_order_init(simple_order, mocked_broker, mocked_fxcm_order):

    full_order = simple_order.get_fxcm_order(broker=mocked_broker, order=mocked_fxcm_order)
    assert full_order is not None


def test_fxcm_order_insertion(simple_order, mocked_broker, mocked_fxcm_order):

    full_order = simple_order.get_fxcm_order(broker=mocked_broker, order=mocked_fxcm_order)
    assert full_order in full_order._trader.orders


def test_fxcm_order_simple_update(simple_order, mocked_broker, mocked_fxcm_order):

    full_order = simple_order.get_fxcm_order(broker=mocked_broker, order=mocked_fxcm_order)

    assert len(full_order._trader.orders) == 1

    full_order.update()


def test_fxcm_order_cancellation(simple_order, mocked_broker, mocked_fxcm_order):

    mocked_fxcm_order.get_status.return_value = 'Canceled'

    full_order = simple_order.get_fxcm_order(broker=mocked_broker, order=mocked_fxcm_order)

    assert len(full_order._trader.orders) == 1

    full_order.update()

    assert len(full_order._trader.orders) == 0


def test_fxcm_order_position(simple_order, mocked_broker, mocked_fxcm_order, mocked_fxcm_position):

    mocked_fxcm_order.get_status.return_value = 'Executing'
    mocked_fxcm_order.get_associated_trade.return_value = mocked_fxcm_position

    full_order = simple_order.get_fxcm_order(broker=mocked_broker, order=mocked_fxcm_order)

    assert len(full_order._trader.orders) == 1

    full_order.update()

    assert len(full_order._trader.orders) == 0
    assert full_order._trader.position is not None

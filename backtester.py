import pandas as pd
from structs import Lots
from typing import List
import uuid


class Position:

    def __init__(self,
                 broker,
                 is_long: bool,
                 size: Lots,
                 entry_price: float,
                 tp_price: float,
                 sl_price: float):

        if is_long:
            assert sl_price < entry_price < tp_price
        else:
            assert tp_price < entry_price < sl_price

        self.broker = broker

        self._is_long = bool(is_long)
        self._entry_price = entry_price
        self._tp_price = tp_price
        self._sl_price = sl_price

        self._size = size

        self._last_price = None
        self._exit_price = None
        self._pct_change = None
        self._pnl = None

        self._closed = False

    def close(self, exit_price: float) -> float:
        self._exit_price = exit_price
        self._closed = True
        self.broker.orders.remove(self)
        return self._pnl

    @property
    def is_long(self):
        return self._is_long

    @property
    def sl(self):
        return self._sl_price

    @sl.setter
    def sl(self, new_sl: float):
        self._sl_price = new_sl

    @property
    def tp(self):
        return self._tp_price

    @tp.setter
    def tp(self, new_tp: float):
        self._tp_price = new_tp

    @property
    def is_closed(self):
        return self._closed


class Order:

    def __init__(self,
                 broker,
                 is_long: bool,
                 size: Lots,
                 limit_price: float,
                 stop_price: float,
                 tp_price: float,
                 sl_price: float,
                 tag=None):

        if is_long:
            assert sl_price < tp_price
        else:
            assert tp_price < sl_price

        self.broker = broker
        self._is_long = is_long
        self._limit = limit_price
        self._stop = stop_price
        self._tp_price = tp_price
        self._sl_price = sl_price

        self._size = size
        self._executed = False

        if tag is None:
            self.tag = str(uuid.uuid1())
        else:
            self.tag = tag

        self.broker.orders.insert(0, self)

    def execute_order(self, entry_price: float):
        self.broker.orders.remove(self)

        position = Position(self.broker,
                            is_long=self.is_long,
                            size=self._size,
                            entry_price=entry_price,
                            tp_price=self._tp_price,
                            sl_price=self._sl_price)

        self.broker.positions.insert(0, position)

    def cancel(self):
        self.broker.orders.remove(self)

    @property
    def is_long(self):
        return self._is_long

    @property
    def tp(self):
        return self._tp_price

    @tp.setter
    def tp(self, new_take_profit):
        self._tp_price = new_take_profit

    @property
    def sl(self):
        return self._sl_price

    @sl.setter
    def sl(self, new_stop_loss):
        self._sl_price = new_stop_loss


class Broker:

    def __init__(self,
                 data: pd.DataFrame,
                 cash: float = 1000.0,
                 spread: float = 1.0,
                 leverage: int = 200):

        self.data = data

        self._cash = cash
        self._spread = spread
        self._leverage = leverage

        self.orders = []
        self.positions = []

    def open_order(self,
                   is_long: bool,
                   limit: float,
                   stop: float,
                   tp: float,
                   sl: float,
                   size: Lots):

        Order(self, is_long=is_long, size=size, limit_price=limit, stop_price=stop, tp_price=tp, sl_price=sl)

    @property
    def open_orders(self) -> List[Order]:
        return self.orders

    @property
    def open_positions(self) -> List[Position]:
        return self.positions

    @property
    def equity(self) -> float:
        return 1

    def historical_price(self, history_len: int):
        pass

import pandas as pd
from structs import Lots
import uuid


class Broker:

    def __init__(self,
                 data: pd.DataFrame,
                 cash: float,
                 spread: float,
                 leverage: int = 50):

        self.data = data

        self._cash = cash
        self._spread = spread
        self._leverage = leverage

        self.orders = []
        self.positions = []

    def get_historical_price(self, history_len: int):
        pass


class Position:

    def __init__(self,
                 broker: Broker,
                 is_long: bool,
                 size: Lots,
                 entry_price: float,
                 tp_price: float,
                 sl_price: float):

        if is_long:
            assert sl_price < entry_price < tp_price
            assert tp_price > sl_price
        else:
            assert tp_price < entry_price < sl_price
            assert tp_price < sl_price

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

    def close(self, exit_price: float):
        self._exit_price = exit_price
        self._closed = True
        self.broker.orders.remove(self)

    def update(self, last_price):
        pass

    @property
    def is_long(self):
        return self._is_long

    @property
    def stop_loss(self):
        return self._sl_price

    @stop_loss.setter
    def stop_loss(self, new_sl: float):
        self._sl_price = new_sl

    @property
    def take_profit(self):
        return self._tp_price

    @take_profit.setter
    def take_profit(self, new_tp: float):
        self._tp_price = new_tp

    @property
    def is_closed(self):
        return self._closed


class Order:

    def __init__(self,
                 broker: Broker,
                 is_long: bool,
                 size: Lots,
                 limit_price: float,
                 stop_price: float,
                 tp_price: float,
                 sl_price: float,
                 tag=None):

        self.broker = broker
        self._is_long = is_long
        self._limit = limit_price
        self._stop = stop_price
        self._tp_price = tp_price
        self._sl_price = sl_price

        self._size = size
        self._fulfilled = False

        if tag is None:
            self.tag = str(uuid.uuid1())
        else:
            self.tag = tag

    def create_position(self, entry_price: float) -> Position:
        self._fulfilled = True
        return Position(broker=self.broker,
                        is_long=self._is_long,
                        size=self._size,
                        entry_price=entry_price,
                        tp_price=self._tp_price,
                        sl_price=self._sl_price)

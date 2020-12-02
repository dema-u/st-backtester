import uuid
import abc
from typing import Optional
from backtester.positions import Position


class Order(metaclass=abc.ABCMeta):

    def __init__(self,
                 broker,
                 is_long: bool,
                 size: int,
                 tp: float,
                 sl: float,
                 tag=None):

        if is_long:
            assert sl < tp
        else:
            assert tp < sl

        self.broker = broker

        self._is_long = bool(is_long)
        self._tp = tp
        self._sl = sl
        self._size = int(size)
        self._executed = False

        self.tag = tag

    def execute_order(self, entry_price: float):
        self.broker.orders.remove(self)

        Position(self.broker,
                 is_long=self.is_long,
                 size=self._size,
                 entry_price=entry_price,
                 tp=self._tp,
                 sl=self._sl,
                 tag=self.tag)

        direction = "Long" if self.is_long else "Short"
        # print(f"Order executed. {direction} position of {self._size} size is opened.")

        self._executed = True

    @property
    def is_long(self):
        return self._is_long

    @property
    def size(self):
        return self._size

    @property
    def is_executed(self):
        return self._executed

    @property
    def tp(self):
        return self._tp

    @tp.setter
    def tp(self, new_take_profit: float):
        self._tp = new_take_profit

    @property
    def sl(self):
        return self._sl

    @sl.setter
    def sl(self, new_stop_loss: float):
        self._sl = new_stop_loss


class MarketOrder(Order):

    def __init__(self,
                 broker,
                 is_long: bool,
                 size: int,
                 tp: float,
                 sl: float,
                 tag=None):
        super(MarketOrder, self).__init__(broker=broker, is_long=is_long, size=size, tp=tp, sl=sl, tag=tag)
        self.broker.orders.insert(0, self)


class EntryOrder(Order):

    def __init__(self,
                 broker,
                 is_long: bool,
                 size: int,
                 limit: Optional[float],
                 stop: Optional[float],
                 tp: float,
                 sl: float,
                 tag=None):

        super(EntryOrder, self).__init__(broker=broker, is_long=is_long, size=size, tp=tp, sl=sl, tag=tag)

        assert ((limit is not None) or (stop is not None))

        if limit is not None:
            raise NotImplemented

        if is_long:
            assert sl < tp
        else:
            assert tp < sl

        self._limit = limit
        self._stop = stop

        self.broker.orders.insert(0, self)

    def cancel(self):
        self.broker.orders.remove(self)

    @property
    def limit(self):
        return self._limit

    @property
    def stop(self):
        return self._stop

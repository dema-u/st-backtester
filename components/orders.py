import uuid
import abc
from structs import Lots
from components.positions import Position


class Order(metaclass=abc.ABCMeta):

    def __init__(self,
                 broker,
                 is_long: bool,
                 size: Lots,
                 tp: float,
                 sl: float,
                 tag=None):

        if is_long:
            assert sl < tp
        else:
            assert tp < sl

        self.broker = broker

        self._is_long = is_long
        self._tp = tp
        self._sl = sl
        self._size = size
        self._executed = False

        if tag is None:
            self.tag = str(uuid.uuid1())
        else:
            self.tag = tag

    def execute_order(self, entry_price: float):
        self.broker.orders.remove(self)

        Position(self.broker,
                 is_long=self.is_long,
                 size=self._size,
                 entry_price=entry_price,
                 tp=self._tp,
                 sl=self._sl)

        self._executed = True

    @property
    def is_long(self):
        return self._is_long

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
                 size: Lots,
                 tp: float,
                 sl: float,
                 tag=None):
        super(MarketOrder, self).__init__(broker=broker, is_long=is_long, size=size, tp=tp, sl=sl, tag=tag)
        self.broker.orders.insert(0, self)


class EntryOrder(Order):

    def __init__(self,
                 broker,
                 is_long: bool,
                 size: Lots,
                 limit: float,
                 stop: float,
                 tp: float,
                 sl: float,
                 tag=None):

        super(EntryOrder, self).__init__(broker=broker, is_long=is_long, size=size, tp=tp, sl=sl, tag=tag)

        if is_long:
            assert sl < tp
        else:
            assert tp < sl

        self._limit = limit
        self._stop = stop

        self.broker.orders.insert(0, self)

    def cancel(self):
        self.broker.orders.remove(self)

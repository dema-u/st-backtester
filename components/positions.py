from structs import Lots


class Position:

    def __init__(self,
                 broker,
                 is_long: bool,
                 size: Lots,
                 entry_price: float,
                 tp: float,
                 sl: float):

        if is_long:
            assert sl < entry_price < tp
        else:
            assert tp < entry_price < sl

        self.broker = broker

        self._is_long = bool(is_long)
        self._entry_price = entry_price
        self._tp = tp
        self._sl = sl

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
        return self._sl

    @sl.setter
    def sl(self, new_sl: float):
        self._sl = new_sl

    @property
    def tp(self):
        return self._tp

    @tp.setter
    def tp(self, new_tp: float):
        self._tp = new_tp

    @property
    def is_closed(self):
        return self._closed
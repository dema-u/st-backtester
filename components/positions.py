

class Position:

    def __init__(self,
                 broker,
                 is_long: bool,
                 size: int,
                 entry_price: float,
                 tp: float,
                 sl: float,
                 tag: str):

        if is_long:
            assert sl < entry_price < tp
        else:
            assert tp < entry_price < sl

        self.broker = broker

        self._is_long = bool(is_long)
        self._entry_price = entry_price
        self._tp = tp
        self._sl = sl
        self._tag = tag

        self._size = int(size)

        self._latest_price = None
        self._exit_price = None
        self._pct_change = None
        self._pnl = None

        self._closed = False
        self.isback = False

        self.broker.positions.insert(0, self)

    def close(self) -> float:

        self._closed = True
        self._exit_price = self._latest_price

        self.broker.positions.remove(self)

        return self._pnl

    def update(self, latest_price: float):

        self._latest_price = latest_price

        if self.is_long:
            assert (self.tp >= latest_price >= self.sl)
            pct_change = (latest_price - self.entry_price) / self.entry_price
        else:
            assert (self.tp <= latest_price <= self.sl)
            pct_change = (self.entry_price - latest_price) / self.entry_price

        self._pnl = (self._size * 1000) * pct_change

    @property
    def is_long(self):
        return self._is_long

    @property
    def size(self):
        return self._size

    @property
    def entry_price(self):
        return self._entry_price

    @property
    def pnl(self):
        return self._pnl

    @property
    def is_closed(self):
        return self._closed

    @property
    def tag(self):
        return self._tag

    @property
    def sl(self):
        return self._sl

    @sl.setter
    def sl(self, new_sl: float):

        if self.is_long:
            assert new_sl < self._latest_price < self.tp
        else:
            assert self.tp < self._latest_price < new_sl

        self._sl = new_sl

    @property
    def tp(self):
        return self._tp

    @tp.setter
    def tp(self, new_tp: float):

        if self.is_long:
            assert self.sl < self._latest_price < new_tp
        else:
            assert new_tp < self._latest_price < self.sl

        self._tp = new_tp

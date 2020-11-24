class CurrencyPair:

    JPY_PRECISION = 3
    PRECISION = 5

    def __init__(self, pair: str):

        if len(pair) == 7 and pair[4] == '/':
            pair = pair.replace('/', '')

        assert len(pair) == 6, "Currency name is incorrect format!"

        self._pair = pair
        self.num_currency = pair[:3]
        self.den_currency = pair[3:]

    @property
    def price_precision(self):
        if self.num_currency == 'JPY' or self.den_currency == 'JPY':
            return self.JPY_PRECISION
        else:
            return self.PRECISION

    @property
    def name(self):
        return self._pair

    @property
    def fxcm_name(self):
        return self.num_currency + '/' + self.den_currency


class Pips:

    pip_standard = 0.0001
    pip_jpy = 0.01

    def __init__(self, pips: float, jpy_pair: bool = False):
        self.pips = pips
        self.jpy_pair = jpy_pair

    @property
    def price_units(self) -> float:
        return self.pips * self.pip_standard if (not self.jpy_pair) else self.pips * self.pip_jpy

    def __add__(self, other):
        assert isinstance(other, Pips)
        return Pips(self.pips + other.pips)

    def __sub__(self, other):
        assert isinstance(other, Pips)
        return Pips(self.pips - other.pips)

    def __repr__(self):
        return f"Pips({self.pips})"


class MilliLots:

    LOT = 1000
    MIN_LOT = 1

    def __init__(self, lots: float):
        self.lots = lots

    @property
    def units(self):
        return self.lots * MilliLots.LOT

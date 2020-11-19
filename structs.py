

class Pips:

    pip_standard = 0.0001
    pip_jpy = 0.01

    def __init__(self, pips: int, jpy_pair: bool = False):
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


class Lots:

    LOT = 100000
    MIN_LOT = 0.01

    def __init__(self, lots: float):
        self.lots = lots

    @property
    def units(self):
        return self.lots * Lots.LOT

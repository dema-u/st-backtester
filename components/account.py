

class Account:

    LOT = 1000
    MIN_LOT = 1

    def __init__(self, broker, cash: float, leverage: int):

        self.broker = broker

        self.initial_cash = cash

        self._cash = cash
        self._leverage = leverage

    def reset(self):
        self._cash = self.initial_cash

    def process_pnl(self, pnl: float) -> None:
        self._cash += pnl

    @property
    def leverage(self):
        return self._leverage

    @property
    def used_margin(self) -> float:
        total_amount_positions = sum((position.size for position in self.broker.positions)) * 1000
        return total_amount_positions / self.leverage

    @property
    def available_margin(self) -> float:
        return self._cash - self.used_margin

    @property
    def available_size(self) -> float:
        return (self.available_margin * self.leverage) / self.LOT

    @property
    def equity(self) -> float:
        total_pnl = sum((position.pnl for position in self.broker.positions))
        return total_pnl + self._cash

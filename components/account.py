

class Account:

    LOT = 1000
    MIN_LOT = 1

    def __init__(self, broker, cash: float, leverage: int):

        self.broker = broker

        self._cash = cash
        self._leverage = leverage

    def process_pnl(self, pnl: float) -> None:
        self._cash += pnl

    @property
    def available_margin(self):
        total_amount_positions = sum((position.size for position in self.broker.positions)) * 1000
        total_amount = self._cash * self._leverage

        return (total_amount - total_amount_positions) / self._leverage

    @property
    def available_size(self):
        return (self.available_margin * self._leverage) / self.LOT

    @property
    def equity(self):
        total_pnl = sum((position.pnl for position in self.broker.positions))
        return total_pnl + self._cash


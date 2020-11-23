import pandas as pd
from structs import Lots
from typing import List
from components.orders import GeneralOrder, MarketOrder
from components.positions import Position


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

    def open_general_order(self,
                           is_long: bool,
                           limit: float,
                           stop: float,
                           tp: float,
                           sl: float,
                           size: Lots):
        GeneralOrder(self, is_long=is_long, size=size, limit=limit, stop=stop, tp=tp, sl=sl)

    def open_market_order(self,
                          is_long: bool,
                          tp: float,
                          sl: float,
                          size: Lots):
        MarketOrder(self, is_long=is_long, size=size, tp=tp, sl=sl)

    @property
    def open_orders(self) -> List[MarketOrder, GeneralOrder]:
        return self.orders

    @property
    def open_positions(self) -> List[Position]:
        return self.positions

    @property
    def equity(self) -> float:
        return 1

    def historical_price(self, history_len: int):
        pass

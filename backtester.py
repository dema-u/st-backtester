import pandas as pd
from structs import Lots
from typing import List
from components.orders import EntryOrder, MarketOrder
from components.positions import Position


class Broker:

    def __init__(self,
                 data: pd.DataFrame,
                 cash: float = 1000.0,
                 spread: float = 1.0,
                 leverage: int = 50):

        self.data = data

        self._cash = cash
        self._equity = cash
        self._leverage = leverage

        self._spread = spread

        self.orders = []
        self.positions = []

        self.index = 0
        self.start_index = self.index
        self.end_index = len(data)

    def open_entry_order(self,
                         is_long: bool,
                         limit: float,
                         stop: float,
                         tp: float,
                         sl: float,
                         size: Lots):
        EntryOrder(self, is_long=is_long, size=size, limit=limit, stop=stop, tp=tp, sl=sl)

    def open_market_order(self,
                          is_long: bool,
                          tp: float,
                          sl: float,
                          size: Lots):
        MarketOrder(self, is_long=is_long, size=size, tp=tp, sl=sl)

    @property
    def open_orders(self) -> List[MarketOrder, EntryOrder]:
        return self.orders

    @property
    def open_positions(self) -> List[Position]:
        return self.positions

    @property
    def equity(self) -> float:
        return self._equity

    @property
    def cash(self) -> float:
        return self._cash

    def get_price(self, history_len: int):
        pass

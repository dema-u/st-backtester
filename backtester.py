import pandas as pd
from typing import List
from datetime import datetime
from components.orders import EntryOrder, MarketOrder
from components.positions import Position
from components.account import Account


class Broker:

    def __init__(self,
                 data: pd.DataFrame,
                 cash: float = 1000.0,
                 leverage: int = 50):

        self.data = data

        self.account = Account(self, cash, leverage)

        self.orders = []
        self.positions = []

    def open_entry_order(self,
                         is_long: bool,
                         limit: float,
                         stop: float,
                         tp: float,
                         sl: float,
                         size: int,
                         tag: str = None):

        if size > self.available_size:
            message = f'Not enough cash to submit this trade. Available {self.available_size}, Requested: {size}'
            raise AttributeError(message)

        EntryOrder(self, is_long=is_long, size=size, limit=limit, stop=stop, tp=tp, sl=sl, tag=tag)

    def open_market_order(self,
                          is_long: bool,
                          tp: float,
                          sl: float,
                          size: int,
                          tag: str = None):

        if size > self.available_size:
            message = f'Not enough cash to submit this trade. Available {self.available_size}, Requested: {size}'
            raise AttributeError(message)

        MarketOrder(self, is_long=is_long, size=size, tp=tp, sl=sl, tag=tag)

    @property
    def equity(self) -> float:
        return self.account.equity

    @property
    def available_size(self) -> float:
        return self.account.available_size

    @property
    def current_time(self) -> datetime:
        return datetime(2020, 1, 1)

    def get_prices(self, history_len: int, bid_ask: str):
        pass

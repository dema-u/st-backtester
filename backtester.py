import pandas as pd
from components.orders import EntryOrder, MarketOrder
from components.account import Account


class Broker:

    def __init__(self,
                 data: pd.DataFrame,
                 cash: float = 1000.0,
                 leverage: int = 50):

        self._data = data

        self.account = Account(self, cash, leverage)

        self.orders = []
        self.positions = []

        self._index = 0
        self._end_index = len(data)

    def reset(self):

        self.account.reset()

        self.orders = []
        self.positions = []

        self._index = 0

    def next(self):
        self._process_orders()
        self._process_positions()

    def _process_orders(self):

        prices = self._current_prices

        long_entry_orders = [order for order in self.orders if order.is_long and isinstance(order, EntryOrder)]
        short_entry_orders = [order for order in self.orders if (not order.is_long) and isinstance(order, EntryOrder)]

        long_market_orders = [order for order in self.orders if order.is_long and isinstance(order, MarketOrder)]
        short_market_orders = [order for order in self.orders if (not order.is_long) and isinstance(order, MarketOrder)]

        for long_market_order in long_market_orders:
            long_market_order.execute_order(entry_price=prices['OpenBid'])

        for short_market_order in short_market_orders:
            short_market_order.execute_order(entry_price=prices['OpenAsk'])

        # Check against bid prices
        for long_entry_order in long_entry_orders:
            pass

        # Check against ask prices
        for short_entry_order in short_entry_orders:
            pass

    def _process_positions(self):

        prices = self._current_prices

        long_positions = [position for position in self.positions if position.is_long]
        short_positions = [position for position in self.positions if (not position.is_long)]

        # Need to sell, so check against ask prices
        for long_position in long_positions:
            pass

        # Need to buy, so check against bid prices
        for short_position in short_positions:
            pass

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

    def get_historical_prices(self, history_len: int = 24) -> pd.DataFrame:
        return self._data.iloc[self._index - history_len:self._index]

    @property
    def equity(self) -> float:
        return self.account.equity

    @property
    def available_size(self) -> float:
        return self.account.available_size

    @property
    def current_time(self) -> pd.Timestamp:
        return self._data.index[self._index]

    @property
    def current_spread(self):
        current_prices = self._current_prices
        return current_prices['BidClose'] - current_prices['AskClose']

    @property
    def _current_prices(self) -> pd.Series:
        return self._data.iloc[self._index]

import pandas as pd
from components.orders import EntryOrder, MarketOrder
from components.account import Account


class Broker:

    def __init__(self,
                 data: pd.DataFrame,
                 cash: float = 1000.0,
                 leverage: int = 50):

        assert len(data.columns) == 8

        self._data = data

        self.account = Account(self, cash, leverage)

        self.orders = []
        self.positions = []

        self._index = 0
        self._end_index = len(data)

        self.equity_history = [self.equity]

    def reset(self):

        self.account.reset()

        self.orders = []
        self.positions = []

        self._index = 0

    def next(self):
        self._process_orders()
        self._process_positions()

        self.equity_history.append(self.equity)

    def _process_orders(self):

        prices = self._current_prices

        long_market_orders = [order for order in self.orders if order.is_long and isinstance(order, MarketOrder)]
        short_market_orders = [order for order in self.orders if (not order.is_long) and isinstance(order, MarketOrder)]

        for long_market_order in long_market_orders:
            long_market_order.execute_order(entry_price=prices['OpenBid'])

        for short_market_order in short_market_orders:
            short_market_order.execute_order(entry_price=prices['OpenAsk'])

        long_entry_orders = [order for order in self.orders if order.is_long and isinstance(order, EntryOrder)]
        short_entry_orders = [order for order in self.orders if (not order.is_long) and isinstance(order, EntryOrder)]

        for long_entry_order in long_entry_orders:
            bid_high, bid_low = prices['HighBid'], prices['LowBid']

            if bid_low < long_entry_order.stop < bid_high:
                long_entry_order.execute_order(long_entry_order.stop)

        for short_entry_order in short_entry_orders:
            ask_high, ask_low = prices['HighAsk'], prices['LowAsk']

            if ask_low < short_entry_order.stop < ask_high:
                short_entry_order.execute_order(short_entry_order.stop)

    def _process_positions(self):

        prices = self._current_prices

        long_positions = [position for position in self.positions if position.is_long]
        short_positions = [position for position in self.positions if (not position.is_long)]

        # Need to sell, so check against ask prices
        for long_position in long_positions:
            ask_high, ask_low, ask_close = prices['HighAsk'], prices['LowAsk'], prices['CloseAsk']

            if ask_low < long_position.tp < ask_high:
                long_position.update(long_position.tp)
                position_pnl = long_position.close()
                self.account.process_pnl(position_pnl)

            elif ask_low < long_position.sl < ask_high:
                long_position.update(long_position.sl)
                position_pnl = long_position.close()
                self.account.process_pnl(position_pnl)

            else:
                long_position.update(ask_close)

        # Need to buy, so check against bid prices
        for short_position in short_positions:
            bid_high, bid_low, bid_close = prices['HighBid'], prices['LowBid'], prices['CloseBid']

            if bid_low < short_position.tp < bid_high:
                short_position.update(short_position.tp)
                position_pnl = short_position.close()
                self.account.process_pnl(position_pnl)

            elif bid_low < short_position < bid_high:
                short_position.update(short_position.sl)
                position_pnl = short_position.close()
                self.account.process_pnl(position_pnl)

            else:
                short_position.update(bid_close)

    def open_entry_order(self,
                         is_long: bool,
                         limit: float,
                         stop: float,
                         tp: float,
                         sl: float,
                         size: int,
                         tag: str = None):

        if size > self.available_size:
            message = f'Not enough cash to submit this order. Available {self.available_size}, Requested: {size}.'
            raise AttributeError(message)

        EntryOrder(self, is_long=is_long, size=size, limit=limit, stop=stop, tp=tp, sl=sl, tag=tag)

    def open_market_order(self,
                          is_long: bool,
                          tp: float,
                          sl: float,
                          size: int,
                          tag: str = None):

        if size > self.available_size:
            message = f'Not enough cash to submit this order. Available {self.available_size}, Requested: {size}.'
            raise AttributeError(message)

        MarketOrder(self, is_long=is_long, size=size, tp=tp, sl=sl, tag=tag)

    def get_historical_prices(self, history_len: int = 24) -> pd.DataFrame:
        return self._data.iloc[self._index - history_len:self._index]

    @property
    def leverage(self):
        return self.account.leverage

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
    def historical_equity(self):
        return pd.Series(data=self.equity_history, index=self._data.index)

    @property
    def _current_prices(self) -> pd.Series:
        return self._data.iloc[self._index]

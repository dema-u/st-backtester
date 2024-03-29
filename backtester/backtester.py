import pandas as pd
from typing import Optional
from backtester.orders import EntryOrder, MarketOrder
from backtester.account import Account


class Broker:

    def __init__(self,
                 data: pd.DataFrame,
                 cash: float = 1000.0,
                 leverage: int = 30):

        self._data = data

        self.account = Account(self, cash, leverage)

        self.orders = []
        self.positions = []

        self._index = 0
        self._end_index = len(data)

        self._equity_history = [self.equity]

    def reset(self):

        self.account.reset()

        self.orders = []
        self.positions = []

        self._index = 0

    def next(self):

        self._index += 1

        self._process_orders()
        self._process_positions()

        self._equity_history.append(self.equity)

    def _process_orders(self):

        prices = self.current_prices

        long_market_orders = [order for order in self.orders if order.is_long and isinstance(order, MarketOrder)]
        short_market_orders = [order for order in self.orders if (not order.is_long) and isinstance(order, MarketOrder)]

        for long_market_order in long_market_orders:
            long_market_order.execute_order(entry_price=prices['AskOpen'])

        for short_market_order in short_market_orders:
            short_market_order.execute_order(entry_price=prices['BidOpen'])

        long_entry_orders = [order for order in self.orders if order.is_long and isinstance(order, EntryOrder)]
        short_entry_orders = [order for order in self.orders if (not order.is_long) and isinstance(order, EntryOrder)]

        for long_entry_order in long_entry_orders:
            ask_high, ask_low = prices['AskHigh'], prices['AskLow']

            if ask_low < long_entry_order.stop < ask_high:
                long_entry_order.execute_order(long_entry_order.stop)

        for short_entry_order in short_entry_orders:
            bid_high, bid_low = prices['BidHigh'], prices['BidLow']

            if bid_low < short_entry_order.stop < bid_high:
                short_entry_order.execute_order(short_entry_order.stop)

    def _process_positions(self):

        prices = self.current_prices

        long_positions = [position for position in self.positions if position.is_long]
        short_positions = [position for position in self.positions if (not position.is_long)]

        for long_position in long_positions:

            bid_high, bid_low, bid_close = prices['BidHigh'], prices['BidLow'], prices['BidClose']
            if (bid_low <= long_position.sl <= bid_high) or (bid_low <= long_position.sl >= bid_high):
                #print('long hit sl')
                long_position.update(long_position.sl)
                position_pnl = long_position.close()
                self.account.process_pnl(position_pnl)

            elif (bid_low <= long_position.tp <= bid_high) or (bid_low >= long_position.tp <= bid_high):
                #print('long hit tp')
                long_position.update(long_position.tp)
                position_pnl = long_position.close()
                self.account.process_pnl(position_pnl)

            else:
                long_position.update(bid_close)

            if long_position.tag is not None:
                if bid_low < long_position.tag < bid_high:
                    long_position.isback = True

        for short_position in short_positions:
            ask_high, ask_low, ask_close = prices['AskHigh'], prices['AskLow'], prices['AskClose']

            if (ask_low <= short_position.sl <= ask_high) or (ask_low >= short_position.sl <= ask_high):
                #print('short hit sl')
                short_position.update(short_position.sl)
                position_pnl = short_position.close()
                self.account.process_pnl(position_pnl)

            elif ask_low <= short_position.tp <= ask_high or (ask_low <= short_position.tp >= ask_high):
                #print('short hit tp')
                short_position.update(short_position.tp)
                position_pnl = short_position.close()
                self.account.process_pnl(position_pnl)

            else:
                short_position.update(ask_close)

            if short_position.tag is not None:
                if ask_low < short_position.tag < ask_high:
                    short_position.isback = True

    def open_entry_order(self,
                         is_long: bool,
                         limit: Optional[float],
                         stop: Optional[float],
                         tp: float,
                         sl: float,
                         size: int,
                         tag=None):

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

    def get_historical_prices(self, history_len: int = 120) -> Optional[pd.DataFrame]:
        if self._index < history_len:
            return None
        else:
            return self._data.iloc[self._index-history_len+1:self._index+1]

    @property
    def leverage(self):
        return self.account.leverage

    @property
    def equity(self) -> float:
        return self.account.equity

    @property
    def open_orders(self):
        return list(self.orders)

    @property
    def open_positions(self):
        return list(self.positions)

    @property
    def available_size(self) -> float:
        return self.account.available_size

    @property
    def current_time(self) -> pd.Timestamp:
        return self._data.index[self._index]

    @property
    def current_spread(self):
        current_prices = self.current_prices
        return current_prices['BidClose'] - current_prices['AskClose']

    @property
    def historical_equity(self):
        return self._equity_history

    @property
    def backtest_done(self):
        return self._end_index <= (self._index + 1)

    @property
    def current_prices(self) -> pd.Series:
        return self._data.iloc[self._index]

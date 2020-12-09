import fxcmpy
import datetime
from utils import CurrencyPair, ConfigHandler
from typing import List, Optional, Tuple
from trader.orders import Order, FXCMOrder


RENAMER = {'bidopen': 'BidOpen', 'bidhigh': 'BidHigh', 'bidlow': 'BidLow', 'bidclose': 'BidClose',
           'askopen': 'AskOpen', 'askhigh': 'AskHigh', 'asklow': 'AskLow', 'askclose': 'AskClose'}

COLUMNS = list(RENAMER.values())

FREQ_MAP = {'m1': 1, 'm5': 5}


def _initialize_connection():
    config = ConfigHandler()
    fxcm_section = config.fxcm_settings

    access_token = fxcm_section['access_token']
    log_file = fxcm_section['log_file']
    log_level = fxcm_section['log_level']

    connection = fxcmpy.fxcmpy(access_token=access_token, log_file=log_file, log_level=log_level)

    return connection


def check_connection(function_):
    def _check_connection(*args, **kwargs):
        if not args[0]._connection.is_connected():
            args[0]._connection.connect()
        return function_(*args, **kwargs)

    return _check_connection


class Broker:

    def __init__(self, pair: CurrencyPair, freq: str, logger):

        self._pair = pair
        self._freq = freq

        self._connection = _initialize_connection()

        self.logger = logger

    @check_connection
    def add_callback(self, function_):
        self._connection.subscribe_market_data(self._pair.fxcm_name, (function_,))

    @check_connection
    def place_entry_order(self,
                          order: Order,
                          replace: bool) -> Optional[FXCMOrder]:

        is_long = order.is_long
        entry = round(order.entry, self._pair.price_precision)
        tp = round(order.tp, self._pair.price_precision)
        sl = round(order.sl, self._pair.price_precision)

        if replace:
            if len(self.orders) > 1:
                self.logger.critical('Ambiguous as to which order to pick. Cancelling all and re-adding.')
                self.cancel_all_orders()
            elif len(self.orders) == 1:
                fxcm_order = self.orders[0]

                order_long = fxcm_order.get_isBuy()
                order_tp = fxcm_order.get_limit()
                order_sl = fxcm_order.get_stop()

                if order_long == is_long and order_tp == tp and order_sl == sl:
                    return None
                else:
                    fxcm_order.delete()
        else:
            self.cancel_all_orders()

        entry_order = self._connection.create_entry_order(symbol=self._pair.fxcm_name,
                                                          is_buy=is_long,
                                                          limit=tp,
                                                          rate=entry,
                                                          stop=sl,
                                                          amount=order.size,
                                                          time_in_force='GTC',
                                                          is_in_pips=False)

        return order.get_fxcm_order(broker=self, order=entry_order)

    @check_connection
    def place_oco_order(self,
                        buy_order: Order,
                        sell_order: Order,
                        replace=False) -> Tuple[Optional[FXCMOrder], Optional[FXCMOrder]]:

        buy_fxcm_order, sell_fxcm_order = None, None

        if not replace:
            raise NotImplementedError
        else:
            self.cancel_all_orders()

            oco_order = self._connection.create_oco_order(symbol=self._pair.fxcm_name, time_in_force='GTC',
                                                          amount=buy_order.size,
                                                          is_buy=True, is_buy2=False,
                                                          limit=buy_order.tp, limit2=sell_order.tp,
                                                          rate=buy_order.entry, rate2=sell_order.entry,
                                                          stop=buy_order.sl, stop2=sell_order.sl,
                                                          order_type='MarketRange', at_market=0,
                                                          is_in_pips=False)

            for order in oco_order.get_orders():
                if order.get_isBuy():
                    buy_fxcm_order = buy_order.get_fxcm_order(broker=self, order=order)
                else:
                    sell_fxcm_order = sell_order.get_fxcm_order(broker=self, order=order)

            return buy_fxcm_order, sell_fxcm_order

    @check_connection
    def change_position_sl(self, id, new_sl):
        self._connection.change_trade_stop_limit(id, is_stop=True, rate=new_sl, is_in_pips=False)

    @check_connection
    def cancel_all_positions(self):
        self._connection.close_all_for_symbol(self._pair.fxcm_name)

    @check_connection
    def cancel_all_orders(self):
        for order_id in self._connection.get_order_ids():
            order = self._connection.get_order(order_id)
            order.delete()

    @property
    @check_connection
    def latest_price(self):
        last_price = self._connection.get_last_price(self._pair.fxcm_name)
        return (last_price['Bid'] + last_price['Ask']) / 2

    @property
    @check_connection
    def historical_price(self):

        historical_data = self._connection.get_candles(instrument=self._pair.fxcm_name,
                                                       period=self._freq,
                                                       number=120)

        historical_data = historical_data.rename(RENAMER, axis=1)[COLUMNS]

        now = datetime.datetime.utcnow()

        closest = now - datetime.timedelta(minutes=(now.minute % FREQ_MAP[self._freq]),
                                           seconds=now.second,
                                           microseconds=now.microsecond)

        return historical_data[:closest]

    @property
    @check_connection
    def open_position_ids(self):
        return self._connection.get_open_trade_ids()

    @property
    def open_order_ids(self):
        return self._connection.get_order_ids()

    @property
    @check_connection
    def num_positions(self):
        return len(self.open_position_ids)

    @property
    @check_connection
    def num_orders(self):
        return len(self.open_order_ids)

    @property
    @check_connection
    def available_margin(self):
        return self._connection.get_accounts_summary()['usableMargin3'][0]

    @property
    @check_connection
    def available_equity(self):
        return self._connection.get_accounts_summary()['equity'][0]

    @property
    @check_connection
    def orders(self):
        return [self._connection.get_orders(id) for id in self._connection.get_order_ids()]

    @check_connection
    def close_connection(self):
        self._connection.unsubscribe_market_data(self._pair.fxcm_name)
        self._connection.close()

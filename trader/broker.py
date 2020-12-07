import fxcmpy
import datetime
from utils import CurrencyPair, ConfigHandler


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
        if not args[0].connection.is_connected():
            args[0].connection.connect()
        return function_(*args, **kwargs)
    return _check_connection


class Broker:

    def __init__(self, pair: CurrencyPair, freq: str):

        self._pair = pair
        self._freq = freq

        self._connection = _initialize_connection()

    @check_connection
    def add_callback(self, function_):
        self._connection.subscribe_market_data(self._pair.fxcm_name, (function_, ))

    @check_connection
    def place_oco_order(self, allow_duplicate=True):
        pass

    @check_connection
    def place_entry_order(self, allow_duplicate=True):
        pass

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
    def historical_price(self, length: int):

        historical_data = self._connection.get_candles(instrument=self._pair.fxcm_name,
                                                       period=self._freq,
                                                       number=length)

        historical_data = historical_data.rename(RENAMER, axis=1)[COLUMNS]

        now = datetime.datetime.utcnow()

        closest = now - datetime.timedelta(minutes=(now.minute % FREQ_MAP[self._freq]),
                                           seconds=now.second,
                                           microseconds=now.microsecond)

        return historical_data[:closest]

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
    def num_positions(self):
        return len(self._connection.get_open_trade_ids())

    @property
    @check_connection
    def num_orders(self):
        return len(self._connection.get_order_ids())

    @check_connection
    def close_connection(self):
        self._connection.unsubscribe_market_data(self._pair.fxcm_name)
        self._connection.close()

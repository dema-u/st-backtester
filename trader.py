import os
import fxcmpy
import configparser
import schedule
import time
from typing import List
from datetime import datetime
from strategy.fractals import FractalStrategy
from structs import CurrencyPair, Pips


RENAMER = {'bidopen': 'BidOpen', 'bidhigh': 'BidHigh', 'bidlow': 'BidLow', 'bidclose': 'BidClose',
           'askopen': 'AskOpen', 'askhigh': 'AskHigh', 'asklow': 'AskLow', 'askclose': 'AskClose'}

COLUMNS = list(RENAMER.keys())


class Trader:

    leverage = 30

    def __init__(self,
                 currency_pair: CurrencyPair,
                 freq: str,
                 strategy: FractalStrategy,
                 logger=None):

        self._pair = currency_pair
        self._freq = freq

        self._strategy = strategy
        self._connection = Trader._initialize_connection()

        self._account_id = self._connection.get_account_ids()[0]
        self._connection.subscribe_market_data(self._pair.fxcm_name)

        self._oco_order = None

        self._logger = logger

    def process_timestep(self):

        upper_fractal, lower_fractal = self._strategy.get_fractals(self.prices)

        if upper_fractal is not None and lower_fractal is not None:
            target_l, back_l, entry_l, sl_l = self._strategy.get_long_order(upper_fractal, lower_fractal)
            target_s, back_s, entry_s, sl_s = self._strategy.get_short_order(upper_fractal, lower_fractal)

            size = self._strategy.get_position_size(self.available_margin, entry_l, sl_l)
            if self._oco_order is not None:
                self.remove_oco_order()

            self._oco_order = self._connection.create_oco_order(symbol=self._pair.fxcm_name, time_in_force='GTC',
                                                                amount=size,
                                                                is_buy=True, is_buy2=False,
                                                                limit=target_l, limit2=target_s,
                                                                rate=entry_l, rate2=entry_s,
                                                                stop=sl_l, stop2=sl_s,
                                                                order_type='MarketRange', at_market=0)

        else:
            self.remove_oco_order()

    @property
    def prices(self):
        historical_data = self._connection.get_candles(instrument=self._pair.fxcm_name, period=self._freq, number=24)
        historical_data = historical_data.rename(RENAMER, axis=1)[COLUMNS]

        time_now = datetime.utcnow()

        return historical_data

    @property
    def available_margin(self):
        return self._connection.get_accounts_summary()['usableMargin3'][0]

    def remove_oco_order(self):
        if self._oco_order is not None:
            for order in self._oco_order.get_orders():
                order.delete()
            self._oco_order = None

    @staticmethod
    def _initialize_connection():
        abspath_api = os.path.abspath('configs/api.ini')
        config = configparser.ConfigParser()
        config.read(abspath_api)

        fxcm_section = config['FXCM']

        access_token = fxcm_section['access_token']
        log_file = fxcm_section['log_file']
        log_level = fxcm_section['log_level']

        connection = fxcmpy.fxcmpy(access_token=access_token, log_file=log_file, log_level=log_level)

        connection.close_all()

        for order in connection.get_orders(kind='list'):
            order.cancel()

        return connection


class ScheduleHelper:

    def __init__(self, time_now, frequency):

        self._time_now = time_now
        self._frequency = frequency

    @property
    def monday(self) -> List[str]:
        pass

    @property
    def tuesday(self) -> List[str]:
        pass

    @property
    def wednesday(self) -> List[str]:
        pass

    @property
    def thursday(self) -> List[str]:
        pass

    @property
    def friday(self) -> List[str]:
        pass


if __name__ == '__main__':

    pair = CurrencyPair('GBPUSD')
    jpy_pair: bool = pair.jpy_pair
    freq = 'm5'

    strategy = FractalStrategy(target_level=4.0,
                               back_level=2.1,
                               break_level=Pips(2, jpy_pair),
                               sl_extension=Pips(1, jpy_pair),
                               max_width=Pips(12, jpy_pair),
                               min_width=Pips(4, jpy_pair),
                               risk=0.0160)

    trader = Trader(currency_pair=pair, strategy=strategy, freq=freq)

    schedule.every().hour.at('00:00')

    while True:
        schedule.run_pending()
        time.sleep(1)


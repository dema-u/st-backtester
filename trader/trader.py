import os
import fxcmpy
import schedule
import time
import datetime
import configparser
import logging
from trader.logger import Logger
from trader.schedule import initialize_schedule
from strategy.fractals import FractalStrategy
from structs import CurrencyPair, Pips

RENAMER = {'bidopen': 'BidOpen', 'bidhigh': 'BidHigh', 'bidlow': 'BidLow', 'bidclose': 'BidClose',
           'askopen': 'AskOpen', 'askhigh': 'AskHigh', 'asklow': 'AskLow', 'askclose': 'AskClose'}

COLUMNS = list(RENAMER.values())


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

        self._longback, self._longback_passed = None, False
        self._shortback, self._shortback_passed = None, False
        self._backlock = False  # this references the back order -> all other variables reference backward order.

        self.close_all_orders()
        self.close_all_positions()

        self._account_id = self._connection.get_account_ids()[0]
        self._connection.subscribe_market_data(self._pair.fxcm_name, (self.flag_back_prices,))

        self._logger = logger

        self.process_timestep()

    def process_timestep(self):

        if len(self._connection.get_order_ids()) == 1 and len(self._connection.get_open_trade_ids()) == 0:
            self.close_all_orders()

        if len(self._connection.get_open_trade_ids()) == 0:  # no positions currently
            self.place_starting_oco()
        else:
            # position is either passed back price or not
            print("Order is already in place.")

    def place_starting_oco(self):

        print('Placing OCO.')

        upper_fractal, lower_fractal = self._strategy.get_fractals(self.prices)

        if (upper_fractal is not None) and (lower_fractal is not None):
            print('Suitable fractals found.')
            target_l, back_l, entry_l, sl_l = self._strategy.get_long_order(upper_fractal, lower_fractal)
            target_s, back_s, entry_s, sl_s = self._strategy.get_short_order(upper_fractal, lower_fractal)
            size = self._strategy.get_position_size(self.available_equity, entry_l, sl_l)

            if entry_s < self.latest_price < entry_l:
                print('Fractals are between entries. Cancelling orders and adding new OCO.')
                if len(self._connection.get_order_ids()) > 0:
                    self.close_all_orders()

                _ = self._connection.create_oco_order(symbol=self._pair.fxcm_name, time_in_force='GTC',
                                                      amount=size,
                                                      is_buy=True, is_buy2=False,
                                                      limit=target_l, limit2=target_s,
                                                      rate=entry_l, rate2=entry_s,
                                                      stop=sl_l, stop2=sl_s,
                                                      order_type='MarketRange', at_market=0,
                                                      is_in_pips=False)

                self._set_back_trades(back_l, back_s)

            else:
                print('Current price is outside of entries, cannot place the orders')

        else:
            print('No suitable fractals. Cancelling orders.')
            self.close_all_orders()
            self._longback, self._shortback = None, None
            self._longback_passed, self._shortback_passed = False, False

    def flag_back_prices(self, _, dataframe):

        # previous_longback, previous_shortback = self._longback_passed, self._shortback_passed

        mid_price = (dataframe.iloc[-1]['Bid'] + dataframe.iloc[-1]['Ask']) / 2

        if self._longback is not None and mid_price > self._longback:
            self._longback_passed = True
        if self._shortback is not None and mid_price < self._shortback:
            self._shortback_passed = True

    def _set_back_trades(self, back_long, back_short) -> None:
        assert back_long > back_short
        self._longback, self._shortback = back_long, back_short

    def _reset_back_trades(self) -> None:
        self._longback, self._shortback = None, None
        self._longback_passed, self._shortback_passed = False, False

    def adjust_stop_loss(self):
        pass

    def close_all_orders(self):
        order_ids = self._connection.get_order_ids()

        for order_id in order_ids:
            order = self._connection.get_order(order_id)
            order.delete()

        self._reset_back_trades()

    def close_all_positions(self):
        position_ids = self._connection.get_open_trade_ids()

        for position_id in position_ids:
            position = self._connection.get_open_position(position_id)
            position.close()

    def close_connection(self):
        self._connection.close()

    @property
    def prices(self):
        historical_data = self._connection.get_candles(instrument=self._pair.fxcm_name, period=self._freq, number=25)
        historical_data = historical_data.rename(RENAMER, axis=1)[COLUMNS]

        now = datetime.datetime.utcnow()

        # TODO: this makes frequency stuff not needed -> need to expand this
        closest = now - datetime.timedelta(minutes=(now.minute % 5) + 5,
                                           seconds=now.second,
                                           microseconds=now.microsecond)

        return historical_data[:closest]

    @property
    def latest_price(self):
        last_price = self._connection.get_last_price(pair.fxcm_name)
        return (last_price['Bid'] + last_price['Ask']) / 2

    @property
    def available_margin(self):
        return self._connection.get_accounts_summary()['usableMargin3'][0]

    @property
    def available_equity(self):
        return self._connection.get_accounts_summary()['equity'][0]

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
            order.delete()

        return connection


if __name__ == '__main__':

    abspath_config = os.path.abspath('configs/trader.ini')

    logger_helper = Logger()
    logger_helper.add_path_handler()
    logger_helper.add_stream_handler()

    config = configparser.ConfigParser()
    config.read(abspath_config)

    trader_section = config['TRADER']

    currency = trader_section['currency']
    frequency = trader_section['frequency']

    target_level = float(trader_section['target_level'])
    back_level = float(trader_section['back_level'])
    break_level = float(trader_section['break_level'])
    sl_extension = float(trader_section['sl_extension'])
    max_width = float(trader_section['max_width'])
    min_width = float(trader_section['min_width'])
    risk = float(trader_section['risk'])

    pair = CurrencyPair(currency)
    jpy_pair: bool = pair.jpy_pair

    strategy = FractalStrategy(target_level=target_level,
                               back_level=back_level,
                               break_level=Pips(break_level, jpy_pair),
                               sl_extension=Pips(sl_extension, jpy_pair),
                               max_width=Pips(max_width, jpy_pair),
                               min_width=Pips(min_width, jpy_pair),
                               risk=risk)

    trader = Trader(currency_pair=pair,
                    strategy=strategy,
                    freq=frequency,
                    logger=logger_helper.logger)

    initialize_schedule(trader)
    logger_helper.logger.info("trader and schedule initialized successfully")

    while True:
        schedule.run_pending()
        time.sleep(1)

import fxcmpy
import schedule
import time
import datetime
from utils import ConfigHandler, LoggerHandler
from trader.components import Order
from trader.schedule import initialize_schedule
from strategy.fractals import FractalStrategy
from structs import CurrencyPair, Pips

RENAMER = {'bidopen': 'BidOpen', 'bidhigh': 'BidHigh', 'bidlow': 'BidLow', 'bidclose': 'BidClose',
           'askopen': 'AskOpen', 'askhigh': 'AskHigh', 'asklow': 'AskLow', 'askclose': 'AskClose'}

COLUMNS = list(RENAMER.values())


class Trader:

    def __init__(self,
                 currency_pair: CurrencyPair,
                 freq: str,
                 strategy: FractalStrategy,
                 logger=None):

        self._pair = currency_pair
        self._freq = freq

        self._strategy = strategy
        self.connection = Trader._initialize_connection()

        self.close_all_positions()
        self.close_all_orders()

        self.orders = []
        self.positions = []
        self.callback_lock = False

        self.close_all_orders()
        self.close_all_positions()

        self._account_id = self.connection.get_account_ids()[0]
        self.connection.subscribe_market_data(self._pair.fxcm_name, (self._process_prices,))

        self.logger = logger

        self.process_timestep()

    def process_timestep(self):

        self.callback_lock = True

        self.logger.debug(f'len(self.positions): {len(self.positions)}')
        self.logger.debug(f'self.num_positions: {self.num_positions}')

        self.logger.debug(f'len(self.orders): {len(self.orders)}')
        self.logger.debug(f'self.num_orders: {self.num_orders}')

        # unforeseen by strategy; could happen if position gets closed and backward offer is hanging.
        if self.num_orders == 1 and self.num_positions == 0:
            self.close_all_orders()

        # unforeseen by strategy; could happen if entry opens before take profit it hit.
        if self.num_positions > 1:
            self.close_all_positions()

        if self.num_positions == 0:  # no positions currently.
            self.place_starting_oco()

        elif self.num_orders == 0 and self.num_positions == 1:  # position is in place, but is it back yet?
            if self.positions[0].is_back:
                self.place_backward_order()

        elif self.num_orders == 1 and self.num_positions == 1:  # we know position is back here.
            self.place_backward_order()

        self.callback_lock = False

    def place_starting_oco(self):

        self.logger.debug('placing OCO order.')

        self.close_all_orders()
        upper_fractal, lower_fractal = self._strategy.get_fractals(self.prices)

        if (upper_fractal is not None) and (lower_fractal is not None):
            target_l, back_l, entry_l, sl_l = self._strategy.get_long_order(upper_fractal, lower_fractal)
            target_s, back_s, entry_s, sl_s = self._strategy.get_short_order(upper_fractal, lower_fractal)
            size = self._strategy.get_position_size(self.available_equity, entry_l, sl_l)

            if entry_s < self.latest_price < entry_l:

                self.logger.info(f'Fractals at {upper_fractal} and {lower_fractal} are between prices')

                if len(self.connection.get_order_ids()) > 0:
                    self.close_all_orders()

                oco_order = self.connection.create_oco_order(symbol=self._pair.fxcm_name, time_in_force='GTC',
                                                             amount=size,
                                                             is_buy=True, is_buy2=False,
                                                             limit=target_l, limit2=target_s,
                                                             rate=entry_l, rate2=entry_s,
                                                             stop=sl_l, stop2=sl_s,
                                                             order_type='MarketRange', at_market=0,
                                                             is_in_pips=False)

                for order in oco_order.get_orders():
                    if order.get_isBuy():
                        Order(trader=self,
                              order=order,
                              back_price=back_l)
                    else:
                        Order(trader=self,
                              order=order,
                              back_price=back_s)

        else:
            self.logger.info('no suitable fractals found for oco order. cancelling all orders.')
            self.close_all_orders()

    def place_backward_order(self):

        self.logger.info('placing backward order. setting position stop loss to entry price')

        self.close_all_orders()
        self.positions[0].sl_to_entry()

        upper_fractal, lower_fractal = self._strategy.get_fractals(self.prices)

        if (upper_fractal is not None) and (lower_fractal is not None):

            assert len(self.positions) == 1

            target_s, back_s, entry_s, sl_s = self._strategy.get_short_order(upper_fractal, lower_fractal)
            target_l, back_l, entry_l, sl_l = self._strategy.get_long_order(upper_fractal, lower_fractal)
            size = self._strategy.get_position_size(self.available_equity, entry_l, sl_l)

            if self.positions[0].is_long:
                entry_order = self.connection.create_entry_order(symbol=pair.fxcm_name,
                                                                 is_buy=False,
                                                                 limit=target_s,
                                                                 rate=entry_s,
                                                                 stop=sl_s,
                                                                 amount=size,
                                                                 time_in_force='GTC',
                                                                 is_in_pips=False)

                self.positions[0].sl = entry_s + Pips(1, jpy_pair=self._pair.jpy_pair).price

                Order(trader=self,
                      order=entry_order,
                      back_price=back_s)

            else:
                entry_order = self.connection.create_entry_order(symbol=pair.fxcm_name,
                                                                 is_buy=True,
                                                                 limit=target_l,
                                                                 rate=entry_l,
                                                                 stop=sl_l,
                                                                 amount=size,
                                                                 time_in_force='GTC',
                                                                 is_in_pips=False)

                self.positions[0].sl = entry_l - Pips(1, jpy_pair=self._pair.jpy_pair).price

                Order(trader=self,
                      order=entry_order,
                      back_price=back_l)
        else:
            self.logger.info('no suitable fractals found for backward order. cancelling all orders.')
            self.close_all_orders()

    def _process_prices(self, _, data):

        if not self.callback_lock:

            mid_price = (data.iloc[-1]['Bid'] + data.iloc[-1]['Ask']) / 2

            for order in list(self.orders):
                order.update(mid_price)

            for position in list(self.positions):
                position.update(mid_price)

    def _adjust_stop_loss(self):
        position_ids = self.connection.get_open_trade_ids()
        trade_id = position_ids[0]
        assert len(position_ids) == 1

        position = self.connection.get_open_position(trade_id)
        entry_price = float(position.get_open())

        self.connection.change_trade_stop_limit(self, is_stop=True, rate=entry_price, is_in_pips=False)

    def close_all_orders(self):

        self.orders = []
        order_ids = self.connection.get_order_ids()

        for order_id in order_ids:
            order = self.connection.get_order(order_id)
            order.delete()

    def close_all_positions(self):

        self.positions = []
        position_ids = self.connection.get_open_trade_ids()

        for position_id in position_ids:
            position = self.connection.get_open_position(position_id)
            position.close()

    def close_connection(self):
        self.connection.close()

    @property
    def prices(self):
        historical_data = self.connection.get_candles(instrument=self._pair.fxcm_name, period=self._freq, number=25)
        historical_data = historical_data.rename(RENAMER, axis=1)[COLUMNS]

        now = datetime.datetime.utcnow()

        # TODO: this makes frequency stuff not needed -> need to expand this
        closest = now - datetime.timedelta(minutes=(now.minute % 5) + 5,
                                           seconds=now.second,
                                           microseconds=now.microsecond)

        return historical_data[:closest]

    @property
    def latest_price(self):
        last_price = self.connection.get_last_price(pair.fxcm_name)
        return (last_price['Bid'] + last_price['Ask']) / 2

    @property
    def available_margin(self):
        return self.connection.get_accounts_summary()['usableMargin3'][0]

    @property
    def available_equity(self):
        return self.connection.get_accounts_summary()['equity'][0]

    @property
    def num_orders(self):
        return len(self.connection.get_order_ids())

    @property
    def num_positions(self):
        return len(self.connection.get_open_trade_ids())

    @staticmethod
    def _initialize_connection():

        config = ConfigHandler()
        fxcm_section = config.fxcm_settings

        access_token = fxcm_section['access_token']
        log_file = fxcm_section['log_file']
        log_level = fxcm_section['log_level']

        connection = fxcmpy.fxcmpy(access_token=access_token, log_file=log_file, log_level=log_level)

        connection.close_all()

        return connection


if __name__ == '__main__':

    config = ConfigHandler()
    trader_section = config.trader_settings

    logger_helper = LoggerHandler()
    logger_helper.add_stream_handler()
    logger_helper.add_path_handler()

    logger = logger_helper.logger

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
                    logger=logger)

    initialize_schedule(trader)
    logger.info('strategy, trader and schedule have been initialized')

    while True:
        schedule.run_pending()
        time.sleep(1)

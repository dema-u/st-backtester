import threading
import schedule
from utils.structs import CurrencyPair, Pips
from strategy import FractalStrategy
from trader.orders import Order
from trader.broker import Broker


RENAMER = {'bidopen': 'BidOpen', 'bidhigh': 'BidHigh', 'bidlow': 'BidLow', 'bidclose': 'BidClose',
           'askopen': 'AskOpen', 'askhigh': 'AskHigh', 'asklow': 'AskLow', 'askclose': 'AskClose'}


COLUMNS = list(RENAMER.values())


class Trader:

    freq_map = {'m1': 1, 'm5': 5}

    def __init__(self,
                 currency_pair: CurrencyPair,
                 freq: str,
                 strategy: FractalStrategy,
                 logger):

        self._pair = currency_pair
        self._freq = freq

        self._strategy = strategy
        self.broker = Broker(currency_pair, freq, logger)

        self.orders = []
        self.position = None
        self.callback_lock = False

        self.broker.cancel_all_orders()
        self.broker.cancel_all_positions()

        self.broker.add_callback(self._fxcm_callback)

        self.logger = logger

        self.process_timestep()

    def process_timestep(self):

        lock = threading.Lock()
        lock.acquire()

        self._process_prices(self.broker.latest_price)

        if self.broker.num_orders == 1 and self.broker.num_positions == 0:
            self.logger.warning(f'loose order {self.broker.open_order_ids} found, cancelling')
            self.broker.cancel_all_orders()

        if self.broker.num_positions > 1:
            self.logger.warning(f'multiple positions {self.broker.open_position_ids} found, cancelling')
            self.broker.cancel_all_positions()

        if self.broker.num_positions == 0:
            self.logger.info('no positions detected. placing oco order')
            self.place_starting_oco()

        elif self.broker.num_orders == 0 and self.broker.num_positions == 1:
            self.logger.info(f'{self.position.direction} position {self.position.id} in place, reached turn price: {self.position.is_back}')
            if self.position.is_back:
                self.logger.info('placing backward order. setting position stop loss to entry price')
                self.place_backward_order()

        elif self.broker.num_orders == 1 and self.broker.num_positions == 1:
            self.logger.info(f'{self.position.direction} position {self.position.id} in place, reached turn price: {self.position.is_back}')
            if self.position.is_back:
                self.logger.info('placing backward order. setting position stop loss to entry price')
                self.place_backward_order()
            else:
                self.broker.cancel_all_orders()
        else:
            self.logger.critical('unsolved scenario - skipping.')

        lock.release()

        return schedule.CancelJob

    def place_starting_oco(self):

        historical_price = self.broker.historical_price
        upper_fractal, lower_fractal = self._strategy.get_fractals(historical_price)
        upper_date, lower_date = self._strategy.get_fractals(historical_price, dates=True)

        if (upper_fractal is not None) and (lower_fractal is not None):

            target_l, back_l, entry_l, sl_l = self._strategy.get_long_order(upper_fractal, lower_fractal)
            target_s, back_s, entry_s, sl_s = self._strategy.get_short_order(upper_fractal, lower_fractal)

            size = self._strategy.get_position_size(self.broker.available_equity, entry_l, sl_l)

            if entry_s < self.broker.latest_price < entry_l:

                self.logger.info(f'fractals at {upper_fractal} and {lower_fractal} are between prices, placing oco.')
                self.logger.info(f'upper fractal date: {upper_date}, lower fractal date: {lower_date}')

                long_order = Order(self,
                                   is_long=True,
                                   entry=entry_l,
                                   tp=target_l,
                                   sl=sl_l,
                                   size=size,
                                   back_price=back_l)

                short_order = Order(self,
                                    is_long=False,
                                    entry=entry_s,
                                    tp=target_s,
                                    sl=sl_s,
                                    size=size,
                                    back_price=back_s)
                try:
                    _ = self.broker.place_oco_order(buy_order=long_order, sell_order=short_order, replace=True)
                except IndexError:
                    self.logger.error('Index error while placing oco, skipping timestep')

        else:
            self.logger.info('no suitable fractals found for oco order. cancelled all orders.')
            self.broker.cancel_all_orders()

    def place_backward_order(self):

        self.position.sl = self.position.open_price

        historical_price = self.broker.historical_price
        upper_fractal, lower_fractal = self._strategy.get_fractals(historical_price)
        upper_date, lower_date = self._strategy.get_fractals(historical_price, dates=True)

        if (upper_fractal is not None) and (lower_fractal is not None):

            target_s, back_s, entry_s, sl_s = self._strategy.get_short_order(upper_fractal, lower_fractal)
            target_l, back_l, entry_l, sl_l = self._strategy.get_long_order(upper_fractal, lower_fractal)

            size = self._strategy.get_position_size(self.broker.available_equity, entry_l, sl_l)

            self.logger.info(f'fractals at {upper_fractal} and {lower_fractal} are between prices, placing oco.')
            self.logger.info(f'upper fractal date: {upper_date}, lower fractal date: {lower_date}')

            if self.position.is_long:

                if self.position.entry < entry_s < self.broker.latest_price:

                    short_order = Order(self,
                                        is_long=False,
                                        entry=entry_s,
                                        tp=target_s,
                                        sl=sl_s,
                                        size=size,
                                        back_price=back_s)

                    try:
                        _ = self.broker.place_entry_order(self, short_order, replace=False)
                        self.position.sl = entry_s + Pips(0.3, jpy_pair=self._pair.jpy_pair).price
                    except IndexError:
                        self.logger.error('Index error while placing oco, skipping timestep')

                else:
                    self.logger.info('sl of long position is above entry, not adding order despite valid fractals.')

            else:

                if self.position.entry > entry_l > self.broker.latest_price:

                    long_order = Order(self,
                                       is_long=True,
                                       entry=entry_l,
                                       tp=target_l,
                                       sl=sl_l,
                                       size=size,
                                       back_price=back_l)


                    try:
                        _ = self.broker.place_entry_order(self, long_order, replace=False)
                        self.position.sl = entry_l - Pips(0.3, jpy_pair=self._pair.jpy_pair).price
                    except IndexError:
                        self.logger.error('Index error while placing oco, skipping timestep')

                else:
                    self.logger.info('sl of short position is below entry, not adding order despite of valid fractals.')
        else:
            self.logger.info('no suitable fractals found for backward order. cancelled all orders.')
            self.broker.cancel_all_orders()

    def _fxcm_callback(self, _, data):
        mid_price = (data.iloc[-1]['Bid'] + data.iloc[-1]['Ask']) / 2
        self._process_prices(mid_price)

    def _process_prices(self, mid_price):

        for order in list(self.orders):
            order.update()

        if self.position is not None:
            self.position.update(mid_price)

    def terminate(self):
        self.broker.cancel_all_orders()
        self.broker.cancel_all_positions()
        self.broker.close_connection()

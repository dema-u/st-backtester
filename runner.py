import pandas as pd
from timeit import default_timer
from backtester import Broker
from strategy.fractals import FractalStrategy
from structs import CurrencyPair, Pips
from utils import DataHandler
from tqdm import tqdm


class StrategyRunner:

    def __init__(self,
                 broker: Broker,
                 corridor: FractalStrategy):

        self._broker = broker
        self._corridor = corridor

    def run(self):
        self.broker.reset()
        self._preprocess_broker()

        position_lock = False

        while not broker.backtest_done:

           #print(
           #    f"{self.broker.current_time}: {round(self.broker.equity, 2)}$. Positions {len(self.broker.positions)}, Orders: {len(self.broker.orders)}")

            historical_prices = self.broker.get_historical_prices(history_len=24)

            if len(self.broker.open_positions) == 0 and len(self.broker.open_orders) == 0:
                position_lock = False
                upper_fractal, lower_fractal = self.corridor.get_fractals(historical_prices)
                if upper_fractal is not None and lower_fractal is not None:
                    self._place_starting_orders(upper_fractal, lower_fractal)

            elif len(self.broker.open_positions) == 0 and len(self.broker.open_orders) == 2:
                position_lock = False
                upper_fractal, lower_fractal = self.corridor.get_fractals(historical_prices)
                if upper_fractal is not None and lower_fractal is not None:
                    self._place_starting_orders(upper_fractal, lower_fractal)

            elif len(self.broker.open_positions) == 1 and len(self.broker.open_orders) == 1 and (not position_lock):
                position_lock = True
                for order in self.broker.open_orders:
                    order.cancel()

            elif len(self.broker.open_positions) == 1 and len(self.broker.open_orders) == 1 and position_lock:
                upper_fractal, lower_fractal = self.corridor.get_fractals(historical_prices)
                if upper_fractal is not None and lower_fractal is not None:
                    self._place_opposite_order(upper_fractal, lower_fractal)

            elif len(self.broker.open_positions) == 1 and len(self.broker.open_orders) == 0:
                if self.broker.positions[0].isback:

                    upper_fractal, lower_fractal = self.corridor.get_fractals(historical_prices)
                    position = self.broker.positions[0]

                    position.sl = position.entry_price

                    if upper_fractal is not None and lower_fractal is not None:
                        self._place_opposite_order(upper_fractal, lower_fractal)

            elif len(self.broker.orders) == 1 and len(self.broker.positions) == 0:
                for order in self.broker.open_orders:
                    order.cancel()

            elif len(self.broker.positions) == 2:
                for position in self.broker.open_positions:
                    position.close()

            else:
                print(f"Case not covered. Orders: {len(self.broker.orders)}, Positions: {len(self.broker.positions)}")

            self.broker.next()

    def _place_opposite_order(self, upper_fractal, lower_fractal):
        position = self.broker.positions[0]

        if position.is_long:
            target, back, entry, sl = self.corridor.get_short_order(upper_fractal, lower_fractal)
            order_long = False
        else:
            target, back, entry, sl = self.corridor.get_long_order(upper_fractal, lower_fractal)
            order_long = True

        position.sl = entry
        capital = self.broker.account.available_margin
        size = self.corridor.get_position_size(capital=capital, entry=entry, sl=sl)

        for order in self.broker.open_orders:
            order.cancel()

        # print(f'Placing backward offer! Size: {size}, position size: {position.size}')

        self.broker.open_entry_order(is_long=order_long,
                                     limit=None,
                                     stop=entry,
                                     tp=target,
                                     sl=sl,
                                     size=size,
                                     tag=back)

    def _place_starting_orders(self, upper_fractal, lower_fractal):
        # print("Placing starting order!")
        target_l, back_l, entry_l, sl_l = self.corridor.get_long_order(upper_fractal, lower_fractal)
        target_s, back_s, entry_s, sl_s = self.corridor.get_short_order(upper_fractal, lower_fractal)

        capital = self.broker.account.available_margin

        size = self.corridor.get_position_size(capital=capital, entry=entry_l, sl=sl_l)

        for order in self.broker.open_orders:
            order.cancel()

        self.broker.open_entry_order(is_long=True,
                                     limit=None,
                                     stop=entry_l,
                                     tp=target_l,
                                     sl=sl_l,
                                     size=size,
                                     tag=back_l)

        self.broker.open_entry_order(is_long=False,
                                     limit=None,
                                     stop=entry_s,
                                     tp=target_s,
                                     sl=sl_s,
                                     size=size,
                                     tag=back_s)

    def _preprocess_broker(self):

        price = None

        while price is None:
            price = self.broker.get_historical_prices()
            self.broker.next()

    @property
    def broker(self):
        return self._broker

    @property
    def corridor(self):
        return self._corridor


if __name__ == '__main__':

    pair = CurrencyPair('GBPUSD')
    jpy_pair: bool = pair.jpy_pair
    freq = 'm5'
    year = 2020

    cash = 1000.0
    leverage = 30

    target_level = 4.0
    back_level = 2.0
    break_level = Pips(3, jpy_pair)
    sl_extension = Pips(2, jpy_pair)
    max_width = Pips(12, jpy_pair)
    min_width = Pips(3, jpy_pair)
    risk = 0.020

    results = dict()
    failed_weeks = list()

    data_handler = DataHandler(currency_pair=pair, freq='m5')
    all_weeks = data_handler.get_available_weeks(year=year)
    #all_weeks = [10, 12, 15, 33, 37]

    backtest_start_time = default_timer()

    for week in tqdm(all_weeks):

        data_subset = data_handler.get_week(year, week)

        strategy = FractalStrategy(target_level=target_level,
                                   back_level=back_level,
                                   break_level=break_level,
                                   sl_extension=sl_extension,
                                   max_width=max_width,
                                   min_width=min_width,
                                   risk=risk)

        broker = Broker(data=data_subset,
                        cash=cash,
                        leverage=leverage)

        runner = StrategyRunner(broker=broker,
                                corridor=strategy)

        try:
            runner.run()
        except:
            failed_weeks.append(week)
        finally:
            results[week] = runner.broker.equity

    backtest_end_time = default_timer()
    results_df = pd.DataFrame(results.items(), columns=['Week', 'Equity']).set_index('Week')

    print()
    print('___BACKTEST RESULTS___')
    print(results_df.describe())
    print(results_df)
    print(f'Failed weeks: {failed_weeks}')
    print(f'Backtest time taken {round(backtest_end_time - backtest_start_time, 2)}s')

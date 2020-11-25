import pandas as pd
from backtester import Broker
from strategy.fractals import FractalStrategy
from structs import CurrencyPair, Pips


class StrategyRunner:

    def __init__(self,
                 broker: Broker,
                 corridor: FractalStrategy):
        self._broker = broker
        self._corridor = corridor

    def run(self):
        self._broker.reset()

        while not self.broker.backtest_done:
            broker.next()

    @property
    def broker(self):
        return self._broker

    @property
    def corridor(self):
        return self._corridor


if __name__ == '__main__':

    pair = CurrencyPair('EURUSD')
    jpy_pair: bool = pair.jpy_pair

    cash = 1000.0
    leverage = 30

    target_level = 4.1
    back_level = 2.0
    break_level = Pips(2, jpy_pair)
    sl_extension = Pips(0.5, jpy_pair)
    max_width = Pips(12, jpy_pair)
    min_width = Pips(2, jpy_pair)
    risk = 0.05

    dummy = pd.read_csv('tests/test_data/EURUSD-SAMPLE.csv', index_col=0, parse_dates=True)

    strategy = FractalStrategy(target_level=target_level,
                               back_level=back_level,
                               break_level=break_level,
                               sl_extension=sl_extension,
                               max_width=max_width,
                               min_width=min_width,
                               risk=risk)

    broker = Broker(data=dummy,
                    cash=1000.0,
                    leverage=leverage)

    runner = StrategyRunner(broker=broker,
                            corridor=strategy)

    runner.run()


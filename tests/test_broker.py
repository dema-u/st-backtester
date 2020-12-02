import os
import pytest
import pandas as pd
from backtester.backtester import Broker


@pytest.fixture
def broker():
    file_path = os.path.abspath('test_data/EURUSD-SAMPLE.csv')
    data = pd.read_csv(file_path, index_col=0, parse_dates=True)
    return Broker(data)


def test_historical_data(broker):

    for _ in range(25):
        broker.next()

    current_prices = broker._current_prices
    historical_prices = broker.get_historical_prices(history_len=5)

    current_prices_test = historical_prices.iloc[-1]

    assert current_prices_test['BidClose'] == current_prices['BidClose']
    assert current_prices_test['AskClose'] == current_prices['AskClose']


def test_completion(broker):

    while not broker.backtest_done:
        broker.next()


def test_long_position_execution(broker):

    broker.open_market_order(is_long=True,
                             tp=1.20650,
                             sl=1.20450,
                             size=5)

    broker.next()


def test_short_order_execution(broker):

    broker.open_entry_order(is_long=False,
                            limit=None,
                            stop=1.20550,
                            tp=1.20450,
                            sl=1.20650,
                            size=20)

    for _ in range(25):
        broker.next()


def test_long_order_execution(broker):

    broker.open_entry_order(is_long=True,
                            limit=None,
                            stop=1.20655,
                            tp=1.20750,
                            sl=1.20450,
                            size=20)

    for _ in range(25):
        broker.next()


def test_double_order_cancellation(broker):

    broker.open_entry_order(is_long=True,
                            limit=None,
                            stop=1.20720,
                            tp=1.20750,
                            sl=1.20450,
                            size=20)

    broker.open_entry_order(is_long=False,
                            limit=None,
                            stop=1.20550,
                            tp=1.20450,
                            sl=1.20650,
                            size=25)

    for _ in range(10):
        broker.next()

    broker.orders[0].cancel()


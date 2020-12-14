import pytest
from utils import CurrencyPair
from trader.broker import Broker
from trader.trader import Trader
from strategy.fractals import FractalStrategy
from unittest.mock import Mock, patch
from utils import Pips
from trader import Order


@pytest.fixture
def simple_order():

    trader = Mock()
    trader.orders = []
    trader.position = None

    order = Order(trader=trader,
                  is_long=True,
                  entry=1.0,
                  tp=2.0,
                  sl=0.5,
                  size=5,
                  back_price=1.5)

    return order


@pytest.fixture
def mocked_connection():
    connection_mock = Mock(name='Connection Mock')
    return connection_mock


@pytest.fixture
def mocked_fxcm_order():

    order_mock = Mock(name='Order Mock')
    order_mock.get_isBuy.return_value = 1.0
    order_mock.get_associated_trade.return_value = None

    return order_mock


@pytest.fixture
def mocked_broker(mocked_connection):

    pair = CurrencyPair('EURUSD')
    freq = 'm1'

    with patch('trader.broker._initialize_connection', return_value=mocked_connection):
        broker = Broker(pair, freq)

    return broker


@pytest.fixture
def mocked_trader(mocked_broker, strategy):

    pair = CurrencyPair('EURUSD')
    freq = 'm1'

    with patch('trader.broker.Broker', return_value=mocked_broker):
        trader = Trader(currency_pair=pair, strategy=strategy, freq=freq)

    return trader


@pytest.fixture
def mocked_fxcm_position():

    position_mock = Mock(name='Position Mock')
    position_mock.get_tradeId.return_value = 0

    return position_mock


@pytest.fixture
def strategy():

    pair = CurrencyPair('EURUSD')

    strategy = FractalStrategy(currency_pair=pair,
                               target_level=4.1,
                               back_level=2.0,
                               break_level=Pips(2),
                               sl_extension=Pips(1),
                               max_width=Pips(12),
                               min_width=Pips(2),
                               risk=0.10)
    return strategy

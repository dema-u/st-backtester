import os
import pytest
import pandas as pd
from backtester.backtester import Broker


@pytest.fixture
def broker():
    file_path = os.path.abspath('test_data/EURUSD-SAMPLE.csv')
    data = pd.read_csv(file_path, index_col=0, parse_dates=True)
    return Broker(data)


def test_too_big_size(broker):

    with pytest.raises(AttributeError):
        broker.open_entry_order(is_long=True,
                                limit=None,
                                stop=1.20655,
                                tp=1.20750,
                                sl=1.20450,
                                size=51)

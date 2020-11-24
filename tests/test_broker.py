import pytest
import pandas as pd
from backtester import Broker


@pytest.fixture
def startup_broker():

    data = pd.DataFrame()

    return Broker(data)

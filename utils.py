import os
import pandas as pd
from typing import List
from structs import CurrencyPair
from typing import Tuple


class DataManager:
    _DATA_FOLDER = 'data'

    _RAW_FOLDER = 'raw'
    _CLEAN_FOLDER = 'processed'

    _PRICES_FOLDER = 'prices'

    @staticmethod
    def create_paths(base_data_path):
        os.mkdir(base_data_path)
        os.mkdir(os.path.join(base_data_path, DataManager._RAW_FOLDER))
        os.mkdir(os.path.join(base_data_path, DataManager._CLEAN_FOLDER))
        os.mkdir(os.path.join(base_data_path, DataManager._RAW_FOLDER, DataManager._PRICES_FOLDER))
        os.mkdir(os.path.join(base_data_path, DataManager._CLEAN_FOLDER, DataManager._PRICES_FOLDER))

    @staticmethod
    def store_price_data(data: pd.DataFrame, ticker: str, freq: str, raw: bool) -> None:
        base_data_path = os.path.abspath(DataManager._DATA_FOLDER)

        if not os.path.exists(base_data_path):
            DataManager.create_paths(base_data_path)

        if raw:
            data_path = os.path.join(base_data_path, DataManager._RAW_FOLDER)
        else:
            data_path = os.path.join(base_data_path, DataManager._CLEAN_FOLDER)

        freq_path = os.path.join(data_path, DataManager._PRICES_FOLDER, freq)

        if not os.path.exists(freq_path):
            os.mkdir(freq_path)

        ticker_file = ticker + '.csv'
        full_data_path = os.path.join(freq_path, ticker_file)
        data.to_csv(full_data_path)

    @staticmethod
    def read_price_data(ticker: str, freq: str, raw: bool = False) -> pd.DataFrame:
        base_data_path = os.path.abspath(DataManager._DATA_FOLDER)
        ticker_file = ticker + '.csv'

        if raw:
            data_path = os.path.join(base_data_path, DataManager._RAW_FOLDER)
        else:
            data_path = os.path.join(base_data_path, DataManager._CLEAN_FOLDER)

        file_path = os.path.join(data_path, DataManager._PRICES_FOLDER, freq, ticker_file)

        if os.path.isfile(file_path):
            return pd.read_csv(file_path, index_col=0, parse_dates=True)
        else:
            raise AttributeError("No file found.")

    @staticmethod
    def clean_directories(tickers: List[str], freqs: List[str]):
        raise NotImplementedError


class DataHandler:

    def __init__(self, currency_pair: CurrencyPair, freq: str) -> None:
        self._currency_pair = currency_pair
        self._freq = freq

        data = DataManager.read_price_data(currency_pair.name, freq=freq, raw=False)

        self._data = data[data.index.day_name() != 'Sunday']
        self.years = {n.year: g for n, g in data.groupby(pd.Grouper(level=0, freq='Y'))}

        for year, data in self.years.items():
            self.years[year] = [g for _, g in data.groupby(pd.Grouper(level=0, freq='W'))]

    def get_week(self, year: int, week: int) -> pd.DataFrame:
        assert 0 < week < 52

        return self.years[year][week]

    def get_week_dates(self, year: int, week: int) -> Tuple[pd.Timestamp, pd.Timestamp]:
        start_date = self.years[year][week].index[0]
        end_date = self.years[year][week].index[-1]

        return start_date, end_date

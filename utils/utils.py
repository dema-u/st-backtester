import os
import pandas as pd
import configparser
import logging
from utils.structs import CurrencyPair
from typing import Tuple, List, Optional


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
        assert year in self.get_available_years(), f"No week data for week {week}, {year}"
        assert week in self.get_available_weeks(year), f"No week data for week {week}, {year}"

        return self.years[year][week - 1]

    def get_week_dates(self, year: int, week: int) -> Tuple[pd.Timestamp, pd.Timestamp]:
        start_date = self.years[year][week - 1].index[0]
        end_date = self.years[year][week - 1].index[-1]

        return start_date, end_date

    def get_available_weeks(self, year) -> List[int]:
        return [week + 1 for week in range(len(self.years[year]))]

    def get_available_years(self) -> List[int]:
        return list(self.years.keys())


class ConfigHandler:
    prod_path = os.path.abspath('../configs/settings.prod.ini')
    dev_path = os.path.abspath('../configs/settings.dev.ini')

    def __init__(self):

        self._config = configparser.ConfigParser()

        if os.path.exists(ConfigHandler.dev_path):
            self._config.read(self.dev_path)
        else:
            self._config.read(self.prod_path)

    @property
    def fxcm_settings(self):
        return self._config['FXCM']

    @property
    def data_settings(self):
        return self._config['DATA']

    @property
    def trader_settings(self):
        return self._config['TRADER']


class LoggerHandler:
    filepath_log = os.path.abspath('../logs/trader.log')
    logging_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def __init__(self, name: Optional[str] = None, log_level='INFO'):

        if name is None:
            self._logger = logging.getLogger(__name__)
        else:
            self._logger = logging.getLogger(name)

        self._set_level(log_level)
        self._add_null_handler()

    def add_stream_handler(self) -> None:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(LoggerHandler.logging_format)
        self._logger.addHandler(stream_handler)

    def add_path_handler(self) -> None:
        file_handler = logging.FileHandler(filename=LoggerHandler.filepath_log)
        file_handler.setFormatter(LoggerHandler.logging_format)
        self._logger.addHandler(file_handler)

    def _add_null_handler(self) -> None:
        null_handler = logging.NullHandler()
        null_handler.setFormatter(LoggerHandler.logging_format)
        self._logger.addHandler(null_handler)

    def _set_level(self, level) -> None:
        if level == 'DEBUG':
            self._logger.setLevel(logging.DEBUG)
        elif level == 'INFO':
            self._logger.setLevel(logging.INFO)
        else:
            raise Exception(f'{level} is an invalid log level.')

    @property
    def logger(self):
        return self._logger

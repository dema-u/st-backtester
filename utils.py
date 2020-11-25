import os
import pandas as pd
from typing import List


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

import os
import pandas as pd


class DataManager:

    DATA_FOLDER = 'data'

    RAW_FOLDER = 'raw'
    CLEAN_FOLDER = 'processed'

    PRICES_FOLDER = 'prices'

    @staticmethod
    def create_paths(base_data_path):
        os.mkdir(base_data_path)
        os.mkdir(os.path.join(base_data_path, DataManager.RAW_FOLDER))
        os.mkdir(os.path.join(base_data_path, DataManager.CLEAN_FOLDER))

    @staticmethod
    def store_price_data(data: pd.DataFrame, ticker: str, freq: str, raw: bool) -> None:
        base_data_path = os.path.abspath(DataManager.DATA_FOLDER)

        if not os.path.exists(base_data_path):
            DataManager.create_paths(base_data_path)

        if raw:
            data_path = os.path.join(base_data_path, DataManager.RAW_FOLDER)
        else:
            data_path = os.path.join(base_data_path, DataManager.CLEAN_FOLDER)

        freq_path = os.path.join(data_path, DataManager.PRICES_FOLDER, freq)

        if not os.path.exists(freq_path):
            os.mkdir(freq_path)

        full_data_path = os.path.join(freq_path, ticker)
        data.to_csv(full_data_path)

    @staticmethod
    def read_price_data(ticker: str, freq: str, raw: bool) -> pd.DataFrame:
        base_data_path = os.path.abspath(DataManager.DATA_FOLDER)
        ticker_file = ticker + '.csv'

        if raw:
            data_path = os.path.join(base_data_path, DataManager.RAW_FOLDER)
        else:
            data_path = os.path.join(base_data_path, DataManager.CLEAN_FOLDER)

        file_path = os.path.join(data_path, DataManager.PRICES_FOLDER, freq, ticker_file)

        print(file_path)

        if os.path.isfile(file_path):
            return pd.read_csv(file_path)
        else:
            raise AttributeError("No file found.")

    @staticmethod
    def clean_directories():
        raise NotImplementedError

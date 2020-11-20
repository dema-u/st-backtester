import os
import utils
import configparser
import pandas as pd
from structs import CurrencyPair
from tqdm import tqdm

COLUMNS = ['Open', 'High', 'Low', 'Close']


def mid_price_process(data: pd.DataFrame) -> pd.DataFrame:

    data['Open'] = data['askopen'] + data['bidopen']
    data['High'] = data['askhigh'] + data['bidhigh']
    data['Low'] = data['asklow'] + data['bidlow']
    data['Close'] = data['askclose'] + data['bidclose']

    return data[COLUMNS]


def bid_price_process(data: pd.DataFrame) -> pd.DataFrame:

    data['Open'] = data['askopen']
    data['High'] = data['askhigh']
    data['Low'] = data['asklow']
    data['Close'] = data['askclose']

    return data[COLUMNS]


def ask_price_process(data: pd.DataFrame) -> pd.DataFrame:

    data['Open'] = data['bidopen']
    data['High'] = data['bidhigh']
    data['Low'] = data['bidlow']
    data['Close'] = data['bidclose']

    return data[COLUMNS]


def process_data(data: pd.DataFrame, ticker: CurrencyPair, mode: str) -> pd.DataFrame:

    if mode == 'ask':
        processed_data = ask_price_process(data)
    elif mode == 'bid':
        processed_data = bid_price_process(data)
    else:
        processed_data = mid_price_process(data)

    return processed_data.round(ticker.price_precision)


if __name__ == '__main__':

    abspath_data = os.path.abspath('configs/data.ini')
    config = configparser.ConfigParser()
    config.read(abspath_data)

    data_section = config['DATA']

    all_tickers = [CurrencyPair(ticker) for ticker in data_section['tickers'].split(',')]
    all_freqs = data_section['frequency'].split(',')
    mode = data_section['processing']

    for ticker in tqdm(all_tickers):
        for freq in all_freqs:
            raw_data = utils.DataManager.read_price_data(ticker.name, freq, raw=True)
            processed_data = process_data(raw_data, ticker, mode)
            utils.DataManager.store_price_data(processed_data, ticker.name, freq, raw=False)

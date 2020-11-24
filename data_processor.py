import os
import logging
import utils
import configparser
import pandas as pd
from structs import CurrencyPair

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


COLUMNS = ['Open', 'High', 'Low', 'Close']


RENAMER = {'bidopen': 'BidOpen', 'bidhigh': 'BidHigh', 'bidlow': 'BidLow', 'bidclose': 'BidClose',
           'askopen': 'AskOpen', 'askhigh': 'AskHigh', 'asklow': 'AskLow', 'askclose': 'AskClose'}


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


def bidask_price_process(data: pd.DataFrame) -> pd.DataFrame:

    data = data.rename(RENAMER, axis=1)

    return data[RENAMER.values()]


def process_data(data: pd.DataFrame, ticker: CurrencyPair, mode: str) -> pd.DataFrame:

    if mode == 'ask':
        processed_data = ask_price_process(data)
    elif mode == 'bid':
        processed_data = bid_price_process(data)
    elif mode == 'mid':
        processed_data = mid_price_process(data)
    else:
        processed_data = bidask_price_process(data)

    return processed_data.round(ticker.price_precision)


if __name__ == '__main__':

    abspath_data = os.path.abspath('configs/data.ini')
    abspath_log = os.path.abspath('logs/data.log')
    config = configparser.ConfigParser()
    config.read(abspath_data)

    logger = logging.getLogger("DataProcessing")

    file_handler = logging.FileHandler(filename=abspath_log)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)

    data_section = config['DATA']

    all_tickers = [CurrencyPair(ticker) for ticker in data_section['tickers'].split(',')]
    all_freqs = data_section['frequency'].split(',')
    mode = data_section['processing']
    logger.info(f"Config file read")

    for ticker in tqdm(all_tickers):
        for freq in all_freqs:
            raw_data = utils.DataManager.read_price_data(ticker.name, freq, raw=True)
            processed_data = process_data(raw_data, ticker, mode)
            utils.DataManager.store_price_data(processed_data, ticker.name, freq, raw=False)
            logger.info(f"Ticker {ticker.name} ({freq}) downloaded, processed and stored")

    logger.info(f"Data processing finished")

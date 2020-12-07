import utils
import pandas as pd
from utils.structs import CurrencyPair

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

    raise NotImplementedError

    logger_helper = utils.LoggerHandler()
    logger_helper.add_stream_handler()
    logger = logger_helper.logger

    config = utils.ConfigHandler()
    data_section = config.data_settings

    all_tickers = [CurrencyPair(ticker) for ticker in data_section['tickers'].split(',')]
    all_freqs = data_section['frequency'].split(',')
    mode = data_section['processing']
    logger.info(f"config file read")

    for ticker in tqdm(all_tickers):
        for freq in all_freqs:
            raw_data = utils.DataManager.read_price_data(ticker.name, freq, raw=True)
            processed_data = process_data(raw_data, ticker, mode)
            utils.DataManager.store_price_data(processed_data, ticker.name, freq, raw=False)
            logger.info(f"ticker {ticker.name} ({freq}) downloaded, processed and stored")

    logger.info(f"Data processing finished")

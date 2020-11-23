import os
import logging
import configparser
import pandas as pd
import fxcmpy
import utils
from structs import CurrencyPair
from datetime import datetime

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


FREQ_MAP = {'m5': '5min', 'm15': '15min', 'm30': '30min', 'H1': '1H', 'H4': '4H', 'D1': '1D', 'W1': '1W'}


def get_ticker_data(con, ticker: str, freq: str, first_date: datetime, last_date: datetime) -> pd.DataFrame:
    dates = list(pd.date_range(start=first_date, end=last_date, freq=FREQ_MAP[freq])[::10000]) + [last_date]

    data = [con.get_candles(instrument=ticker, period=freq, start=dates[ix], stop=dates[ix + 1]) for ix in
            range(len(dates) - 1)]

    return pd.concat(data).drop_duplicates()


if __name__ == '__main__':

    abspath_data = os.path.abspath('configs/data.ini')
    abspath_api = os.path.abspath('configs/api.ini')
    abspath_log = os.path.abspath('logs/data.log')

    logger = logging.getLogger("DataCollection")

    file_handler = logging.FileHandler(filename=abspath_log)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)

    config = configparser.ConfigParser()
    config.read(abspath_data)
    config.read(abspath_api)

    fxcm_section = config['FXCM']

    access_token = fxcm_section['access_token']
    log_file = fxcm_section['log_file']
    log_level = fxcm_section['log_level']

    api_con = fxcmpy.fxcmpy(access_token=access_token, log_file=log_file, log_level=log_level)
    logger.info(f"FXCM API connection established")

    data_section = config['DATA']

    all_tickers = [CurrencyPair(ticker) for ticker in data_section['tickers'].split(',')]
    all_freqs = data_section['frequency'].split(',')
    first_date = datetime.strptime(data_section['first_date'], '%d/%m/%Y')
    last_date = datetime.strptime(data_section['last_date'], '%d/%m/%Y')
    logger.info(f"Config file read")

    for ticker in tqdm(all_tickers):
        for freq in all_freqs:
            try:
                save_data = get_ticker_data(api_con,
                                            ticker=ticker.fxcm_name,
                                            freq=freq,
                                            first_date=first_date,
                                            last_date=last_date)

                utils.DataManager.store_price_data(save_data, ticker.name, freq, raw=True)
                logger.info(f"Ticker {ticker.name} ({freq}) downloaded and stored")
            except Exception:
                logger.exception("Exception occurred")

    api_con.close()
    logger.info(f"Data download finished, API connection closed")

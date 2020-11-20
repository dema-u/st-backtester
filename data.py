import os
import configparser
import pandas as pd
import fxcmpy
from datetime import datetime
from utils import DataManager


def get_ticker_data(con, ticker: str, freq: str, first_date: datetime, last_date: datetime) -> pd.DataFrame:
    dates = list(pd.date_range(start=first_date, end=last_date, freq=freq)[::10000]) + [last_date]

    data = [con.get_candles(instrument=ticker, period=freq, start=dates[ix], stop=dates[ix + 1]) for ix in
            range(len(dates) - 1)]

    return pd.concat(data).drop_duplicates()


if __name__ == '__main__':

    abspath_data = os.path.abspath('configs/data.ini')
    abspath_api = os.path.abspath('configs/api.ini')

    config = configparser.ConfigParser()
    config.read(abspath_data)
    config.read(abspath_api)

    fxcm_section = config['FXCM']

    access_token = fxcm_section['access_token']
    log_file = fxcm_section['log_file']
    log_level = fxcm_section['log_level']

    api_con = fxcmpy.fxcmpy(access_token=access_token, log_file=log_file, log_level=log_level)

    data_section = config['DATA']

    all_tickers = data_section['tickers'].split(',')
    all_freqs = data_section['frequency'].split(',')
    first_date = datetime.strptime(data_section['first_date'], '%d/%m/%Y')
    last_date = datetime.strptime(data_section['first_date'], '%d/%m/%Y')

    print(all_tickers)
    print(all_freqs)

    for ticker in all_tickers:
        for freq in all_freqs:
            data = api_con.get_candles(ticker, period=freq)
            print(data)
            print(freq)
            data = get_ticker_data(api_con, ticker=ticker, freq=freq.strip(), first_date=first_date, last_date=last_date)
            DataManager.store_price_data(data, ticker, freq, raw=True)

    print('PROGRAM FINISHED')

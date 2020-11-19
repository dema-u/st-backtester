import os
import configparser
import pandas as pd
import fxcmpy
from datetime import datetime


def get_ticker_data(con, ticker: str, freq: str, first_date: datetime, last_date: datetime) -> pd.DataFrame:
    dates = list(pd.date_range(start=first_date, end=last_date, freq=freq)[::10000]) + [last_date]

    data = [con.get_candles(ticker, period=freq, start=dates[ix], stop=dates[ix + 1]) for ix in
            range(len(dates) - 1)]

    return pd.concat(data).drop_duplicates()


def parse_list(str_list: str) -> list:
    return str_list.split(',')


if __name__ == '__main__':

    abspath_data = os.path.abspath('configs/data.ini')
    abspath_api = os.path.abspath('configs/api.ini')

    config = configparser.ConfigParser()
    config.read(abspath_data)

    api_con = fxcmpy.fxcmpy(abspath_api)

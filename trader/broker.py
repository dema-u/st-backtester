from utils import CurrencyPair


def check_connection(function_):
    def _check_connection(*args, **kwargs):
        if not args[0].connection.is_connected():
            args[0].connection.connect()
        return function_(*args, **kwargs)
    return _check_connection


class Broker:

    def __init__(self, pair: CurrencyPair, freq: str):
        pass

    @check_connection
    def add_callback(self, function_):
        pass

    @check_connection
    def place_oco_order(self, allow_duplicate=True):
        pass

    @check_connection
    def place_entry_order(self, allow_duplicate=True):
        pass

    @check_connection
    def cancel_all_positions(self):
        pass

    @check_connection
    def cancel_all_orders(self):
        pass

    @property
    @check_connection
    def latest_price(self):
        pass

    @property
    @check_connection
    def historical_price(self, length: int):
        pass

    @property
    @check_connection
    def available_margin(self):
        pass

    @property
    @check_connection
    def available_equity(self):
        pass

    @property
    @check_connection
    def num_positions(self):
        pass

    @property
    @check_connection
    def num_orders(self):
        pass

    @check_connection
    def close_connection(self):
        pass

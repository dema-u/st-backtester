import pandas as pd
import numpy as np
from utils.structs import Pips
from typing import Optional, Tuple, Any


class FractalStrategy:

    def __init__(self,
                 target_level: float = 4.1,
                 back_level: float = 2.0,
                 break_level: Pips = Pips(2),
                 sl_extension: Pips = Pips(1),
                 max_width: Pips = Pips(12),
                 min_width: Pips = Pips(2),
                 risk: float = 0.10):

        self._target_level = target_level
        self._back_level = back_level
        self._break_level = break_level
        self._sl_extension = sl_extension
        self._max_width = max_width
        self._min_width = min_width

        self._risk = risk

    def get_long_order(self, upper_fractal: float, lower_fractal: float) -> Tuple[float, float, float, float]:

        if not self.valid_corridor(upper_fractal, lower_fractal):
            raise AttributeError('The submitted corridor is too large or too small.')

        width = upper_fractal - lower_fractal

        back_level = upper_fractal + width * self.back_level
        target_level = upper_fractal + width * self.target_level

        entry_level = upper_fractal + self.break_level.price
        sl_level = lower_fractal - self.sl_extension.price

        return target_level, back_level, entry_level, sl_level

    def get_short_order(self, upper_fractal: float, lower_fractal: float) -> Tuple[float, float, float, float]:

        if not self.valid_corridor(upper_fractal, lower_fractal):
            raise AttributeError('The submitted corridor is too large or too small.')

        width = upper_fractal - lower_fractal

        back_level = lower_fractal - width * self.back_level
        target_level = lower_fractal - width * self.target_level

        entry_level = lower_fractal - self.break_level.price
        sl_level = upper_fractal + self.sl_extension.price

        return target_level, back_level, entry_level, sl_level

    def valid_corridor(self, upper_fractal: float, lower_fractal: float) -> bool:

        width = upper_fractal - lower_fractal

        max_width_price = self.max_width.price
        min_width_price = self.min_width.price

        if min_width_price < width < max_width_price:
            return True
        else:
            return False

    def get_position_size(self, capital: float, entry: float, sl: float) -> int:
        if entry > sl:
            distance_to_sl = (entry - sl) / entry
        else:
            distance_to_sl = (sl - entry) / entry

        position_size = (capital * self._risk) / distance_to_sl

        return int(position_size // 1000)

    def get_fractals(self, historical_price: pd.DataFrame, dates=False) -> Tuple[Optional[Any], Optional[Any]]:

        latest_price = ((historical_price['BidClose'] + historical_price['AskClose']) / 2).iloc[-1]

        processed = pd.DataFrame()

        processed['High'] = (historical_price['BidHigh'] + historical_price['AskHigh']) / 2
        processed['Low'] = (historical_price['BidLow'] + historical_price['AskLow']) / 2

        processed['UpperFractal'] = np.where(
            (processed['High'] > processed['High'].shift(1)) & (processed['High'] > processed['High'].shift(-1)), True,
            False)

        processed['LowerFractal'] = np.where(
            (processed['Low'] < processed['Low'].shift(1)) & (processed['Low'] < processed['Low'].shift(-1)), True,
            False)

        all_upper = processed[processed['UpperFractal'] == True]['High']
        all_lower = processed[processed['LowerFractal'] == True]['Low']

        if len(all_upper) == 0 or len(all_lower) == 0:
            return None, None

        upper_fractal = all_upper.iloc[-1]
        lower_fractal = all_lower.iloc[-1]

        upper_fractal_date = all_upper.index[-1]
        lower_fractal_date = all_lower.index[-1]

        upper_entry = upper_fractal + self.break_level.price
        lower_entry = lower_fractal - self.break_level.price

        if upper_entry > latest_price > lower_entry and self.valid_corridor(upper_fractal, lower_fractal):
            if dates:
                return upper_fractal_date, lower_fractal_date
            else:
                return upper_fractal, lower_fractal
        else:
            return None, None

    @property
    def target_level(self):
        return self._target_level

    @property
    def back_level(self):
        return self._back_level

    @property
    def break_level(self):
        return self._break_level

    @property
    def sl_extension(self):
        return self._sl_extension

    @property
    def max_width(self):
        return self._max_width

    @property
    def min_width(self):
        return self._min_width

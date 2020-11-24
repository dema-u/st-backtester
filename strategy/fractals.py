import pandas as pd
from structs import Pips


class FractalCorridor:

    def __init__(self,
                 target_level: float = 4.1,
                 back_level: float = 2.0,
                 break_level: Pips = Pips(2),
                 sl_extension: Pips = Pips(1),
                 max_width: Pips = Pips(12),
                 min_width: Pips = Pips(2)):

        self._target_level = target_level
        self._back_level = back_level
        self._break_level = break_level
        self._sl_extension = sl_extension
        self._max_width = max_width
        self._min_width = min_width

    def get_long_order(self, upper_fractal: float, lower_fractal: float):

        if self.wide_corrdidor(upper_fractal, lower_fractal):
            raise AttributeError('The submitted corridor is too large or too small.')

        width = upper_fractal - lower_fractal

        back_level = upper_fractal + width * self.back_level
        target_level = upper_fractal + width * self.target_level

        entry_level = upper_fractal + self.break_level.price
        sl_level = lower_fractal - self.sl_extension.price

        return target_level, back_level, entry_level, sl_level

    def get_short_order(self, upper_fractal: float, lower_fractal: float):

        if self.wide_corridor(upper_fractal, lower_fractal):
            raise AttributeError('The submitted corridor is too large or too small.')

        width = upper_fractal - lower_fractal

        back_level = lower_fractal - width * self.back_level
        target_level = lower_fractal - width * self.target_level

        entry_level = lower_fractal - self.break_level.price
        sl_level = upper_fractal + self.sl_extension.price

        return target_level, back_level, entry_level, sl_level

    def wide_corridor(self, upper_fractal: float, lower_fractal: float) -> bool:

        width = upper_fractal - lower_fractal

        max_width_price = self.max_width.price
        min_width_price = self.min_width.price

        if min_width_price < width < max_width_price:
            return False
        else:
            return True

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

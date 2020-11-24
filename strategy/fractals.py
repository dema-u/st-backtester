from structs import Pips


class FractalCorridor:

    def __init__(self,
                 target_level: float = 4.1,
                 back_level: float = 2.0,
                 break_level: Pips = Pips(2.1),
                 sl_extension: Pips = Pips(1),
                 max_width: Pips = Pips(12),
                 min_width: Pips = Pips(2)):

        self._target_level = target_level
        self._back_level = back_level
        self._break_level = break_level
        self._sl_extension = sl_extension
        self._max_width = max_width
        self._min_width = min_width

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

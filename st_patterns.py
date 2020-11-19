import uuid
from structs import Lots
from enum import Enum


class FractalDirection(Enum):
    Up = 1
    Down = 2


class FractalCorridor:

    def __init__(self,
                 upper_fractal: float,
                 lower_fractal: float,
                 breakthrough: float,
                 turn_level: float,
                 target_level: float,
                 tag=None):

        assert upper_fractal > lower_fractal, "Upper fractal < Lower fractal!"
        assert target_level > turn_level, "Target level < Turn level!"

        self.upper_fractal = upper_fractal
        self.lower_fractal = lower_fractal
        self.breakthrough = breakthrough
        self.turn_level = turn_level
        self.target_level = target_level

        if tag is None:
            self.tag = str(uuid.uuid1())
        else:
            self.tag = tag

    def get_order(self, current_price: float, direction: FractalDirection):

        if direction == FractalDirection.Up:
            entry = self.upper_fractal + self.breakthrough
            turn_level = self.upper_fractal + self._turn_level_height

            if current_price > turn_level:
                stop_loss = entry
            else:
                stop_loss = self.lower_fractal

            take_profit = self.upper_fractal + self.target_level

        elif direction == FractalDirection.Down:
            entry = self.lower_fractal - self.breakthrough
            turn_level = self.lower_fractal - self._turn_level_height

            if current_price < turn_level:
                stop_loss = entry
            else:
                stop_loss = self.upper_fractal

            take_profit = self.upper_fractal
        else:
            raise Exception("Should not hit.")

        return 0

    def reached_turn(self, price: float, direction: FractalDirection) -> bool:
        pass

    def reached_target(self, price: float, direction: FractalDirection) -> bool:
        pass

    @property
    def _corridor_width(self) -> float:
        return self.upper_fractal - self.lower_fractal

    @property
    def _turn_level_height(self) -> float:
        return self._corridor_width * self.turn_level

    @property
    def _target_level_height(self) -> float:
        return self._corridor_width * self.target_level

    def __repr__(self):
        _string = '__FRACTAL CORRIDOR__'
        return _string

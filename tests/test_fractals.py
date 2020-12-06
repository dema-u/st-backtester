import pytest
from strategy.fractals import FractalStrategy
from utils.structs import Pips


@pytest.fixture
def corridor():
    corridor = FractalStrategy(target_level=4.1,
                               back_level=2.0,
                               break_level=Pips(2),
                               sl_extension=Pips(1),
                               max_width=Pips(12),
                               min_width=Pips(2),
                               risk=0.10)
    return corridor


def test_width_limit(corridor):
    should_be_true = corridor.valid_corridor(1.20375, 1.20345)

    should_be_false1 = corridor.valid_corridor(1.20355, 1.20345)
    should_be_false2 = corridor.valid_corridor(1.20555, 1.20345)

    assert should_be_true is True

    assert should_be_false1 is False
    assert should_be_false2 is False


def test_position_sizing(corridor):
    size_400 = corridor.get_position_size(1000, 2, 1.5)
    size_300 = corridor.get_position_size(1000, 1.5, 2)

    assert size_400 == 0.0
    assert size_300 == 0.0


def test_incorrect_fractal_short(corridor):
    with pytest.raises(AttributeError):
        corridor.get_short_order(1.1006, 1.1007)


def test_incorrect_fractal_short(corridor):
    with pytest.raises(AttributeError):
        corridor.get_long_order(1.2036, 1.2017)


def test_short_order(corridor):
    target, back, entry, sl = corridor.get_short_order(1.20375, 1.20345)

    assert target < back
    assert back < entry
    assert entry < sl


def test_upper_order(corridor):

    target, back, entry, sl = corridor.get_long_order(1.20375, 1.20345)

    assert target > back
    assert back > entry
    assert entry > sl

import pytest


def test_width_limit(strategy):
    should_be_true = strategy.valid_corridor(1.20375, 1.20345)

    should_be_false1 = strategy.valid_corridor(1.20355, 1.20345)
    should_be_false2 = strategy.valid_corridor(1.20555, 1.20345)

    assert should_be_true is True

    assert should_be_false1 is False
    assert should_be_false2 is False


def test_position_sizing(strategy):
    size_400 = strategy.get_position_size(1000, 2, 1.5)
    size_300 = strategy.get_position_size(1000, 1.5, 2)

    assert size_400 == 0.0
    assert size_300 == 0.0


def test_incorrect_fractal_short(strategy):
    with pytest.raises(AttributeError):
        strategy.get_short_order(1.1006, 1.1007)


def test_incorrect_fractal_short(strategy):
    with pytest.raises(AttributeError):
        strategy.get_long_order(1.2036, 1.2017)


def test_short_order(strategy):
    target, back, entry, sl = strategy.get_short_order(1.20375, 1.20345)

    assert target < back
    assert back < entry
    assert entry < sl


def test_upper_order(strategy):

    target, back, entry, sl = strategy.get_long_order(1.20375, 1.20345)

    assert target > back
    assert back > entry
    assert entry > sl

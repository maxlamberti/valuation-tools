from __future__ import annotations

import numpy as np
from typing import Callable


class RandomValue:

    def __init__(self, values: np.ndarray) -> None:
        self.values = values
        if len(values.shape) == 1:
            self.values.reshape(-1, 1)

    def shape(self) -> tuple[int]:
        return self.values.shape

    def __mul__(self, other: float | RandomValue) -> RandomValue:
        other = other.values if isinstance(other, RandomValue) else other
        return RandomValue(other * self.values)

    def __add__(self, other: float | RandomValue) -> RandomValue:
        other = other.values if isinstance(other, RandomValue) else other
        return RandomValue(self.values + other)

    def __sub__(self, other: float | RandomValue) -> RandomValue:
        other = other.values if isinstance(other, RandomValue) else other
        return RandomValue(self.values - other)

    def __truediv__(self, other: float | RandomValue) -> RandomValue:
        other = other.values if isinstance(other, RandomValue) else other
        return RandomValue(self.values / other)

    def __repr__(self) -> str:
        return self.values.__repr__()

    def __str__(self) -> str:
        return self.values.__str__()

    __rmul__ = __mul__
    __radd__ = __add__
    __floordiv__ = __truediv__


class NormalRv(RandomValue):

    def __init__(self, mean: float, std: float, num_samples: int) -> None:
        self.mean = mean
        self.std = std
        super().__init__(np.random.normal(mean, std, num_samples))


class UniformRv(RandomValue):

    def __init__(self, lower: float, upper: float, num_samples: int) -> None:
        self.lower = lower
        self.upper = upper
        super().__init__(np.random.uniform(lower, upper, num_samples))


class TimeSeriesDistribution(RandomValue):

    def __init__(self, num_samples: int, dist: Callable = None, *args, num_periods: int = None, **kwargs) -> None:

        # dirty override for constructor if want to init from existing numpy array or random value
        if isinstance(num_samples, np.ndarray):
            self.num_periods, self.num_samples = num_samples.shape
            super().__init__(num_samples)
            return
        elif isinstance(num_samples, (RandomValue, TimeSeriesDistribution)):
            self.num_periods, self.num_samples = num_samples.value.shape
            super().__init__(num_samples.values)
            return

        list_args = [len(arg) for arg in args if isinstance(arg, list) or isinstance(arg, np.ndarray)]
        max_arg_shape = max(list_args) if len(list_args) != 0 else None

        if max_arg_shape is not None and num_periods is not None:
            assert max_arg_shape == num_periods, 'Expected list args and num_periods to have same dimensions'
        elif max_arg_shape is not None:
            num_periods = max_arg_shape
        elif num_periods is None:
            num_periods = 1

        self.num_periods = num_periods
        self.num_samples = num_samples

        super().__init__(dist(*args, **kwargs, size=(num_samples, num_periods)))

    def get_values(self, period: int = None) -> np.ndarray:

        if period is None:
            return self.values

        return self.values[:, period]

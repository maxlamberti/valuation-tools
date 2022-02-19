import datetime
import numpy as np


def to_float(x: str) -> float:

    # convert percentage
    if isinstance(x, str) and '%' in x:
        x = x.replace('%', '')
        x = float(x) / 100

    # cast to float
    try:
        result = float(x)
    except (TypeError, ValueError):
        result = np.nan

    return result


def eoy_period_generator(start: datetime.date, end: datetime.date):
    assert end > start, 'Expected end time to be greater than start time.'

    period_time = start.replace(month=12, day=31)
    for period_idx in range(30):
        yield period_idx, period_time
        period_time = period_time.replace(year=period_time.year + 1)
        if period_time > end:
            break

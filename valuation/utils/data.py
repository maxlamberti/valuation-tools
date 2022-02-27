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


def standardize_date(x: str | list | datetime.date | datetime.datetime) -> datetime.date:

    if isinstance(x, list):
        result = [standardize_date(x_i) for x_i in x]
    elif isinstance(x, str):
        x = x.replace('/', '-').replace(' E', '').replace(' A', '')
        if len(x) == 8:
            split_x = x.split('-')
            century = '19' if int(split_x[2]) > 50 else '20'
            x = '-'.join([century + split_x[2], split_x[0], split_x[1]])
        result = datetime.datetime.strptime(x, '%Y-%m-%d').date()
    elif isinstance(x, datetime.datetime):
        result = x.date()
    elif isinstance(x, datetime.date):
        result = x
    else:
        raise ValueError("Do not understand input type {} for input {}".format(type(x), x))

    return result


def eoy_period_generator(start: datetime.date, end: datetime.date):
    assert end > start, 'Expected end time to be greater than start time.'

    period_time = start.replace(month=12, day=31)
    for period_idx in range(30):
        yield period_idx, period_time
        period_time = period_time.replace(year=period_time.year + 1)
        if period_time > end:
            break

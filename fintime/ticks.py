import numpy as np
from matplotlib.dates import (
    DateFormatter,
    DayLocator,
    HourLocator,
    MinuteLocator,
    MonthLocator,
    SecondLocator,
    YearLocator,
)
from fintime.types import Timezone


Locator = DayLocator | HourLocator | YearLocator | MonthLocator | YearLocator


def get_nearest(arr: np.ndarray, value):
    return arr.flat[np.abs(arr - value).argmin()]


def to_secs(td: np.timedelta64) -> int:
    return td.astype("timedelta64[s]").astype(np.int32)


def get_secs_per_inch(ax_span, ax_rel_width: float, width: float):
    ax_width = ax_rel_width * width
    return (ax_span / ax_width).astype(np.int32)


def make_get_locator_and_formatter(tz: Timezone):
    tds_args = [
        (1, "s"),
        (2, "s"),
        (5, "s"),
        (10, "s"),
        (15, "s"),
        (20, "s"),
        (30, "s"),
        (1, "m"),
        (2, "m"),
        (5, "m"),
        (10, "m"),
        (15, "m"),
        (20, "m"),
        (30, "m"),
        (1, "h"),
        (2, "h"),
        (4, "h"),
        (1, "D"),
        (1, "W"),
        (1, "M"),
        (3, "M"),
        (1, "Y"),
    ]

    bins = {}
    secs = []

    for td_args in tds_args:
        td = np.timedelta64(*td_args)
        n_secs = to_secs(td=td)
        if n_secs < to_secs(np.timedelta64(1, "m")):
            locator = SecondLocator(range(0, 60, n_secs), tz=tz)
            formatter = DateFormatter("%H:%M:%S", tz=tz)

        elif n_secs < to_secs(np.timedelta64(60, "m")):
            step = int(n_secs / 60)
            locator = MinuteLocator(range(0, 60, step), tz=tz)
            formatter = DateFormatter("%H:%M", tz=tz)

        elif n_secs < to_secs(np.timedelta64(4, "h")):
            step = int(n_secs / 3600)
            locator = HourLocator(range(0, 24, step), tz=tz)
            formatter = DateFormatter("%d-%H", tz=tz)

        elif n_secs < to_secs(np.timedelta64(1, "D")):
            locator = DayLocator(tz=tz)
            formatter = DateFormatter("%m-%d", tz=tz)
        else:
            locator = DayLocator(interval=5, tz=tz)
            formatter = DateFormatter("%m-%d", tz=tz)

        bins[n_secs] = {"locator": locator, "formatter": formatter}
        secs.append(n_secs)
    secs = np.array(secs)

    def get_locator_and_formatter(
        secs_per_inch: float, nudge: int = 0
    ) -> tuple[Locator, DateFormatter]:
        td_secs = get_nearest(arr=secs, value=secs_per_inch)

        # increase spacing for tick labels that contain more characters
        if td_secs <= 60:
            nudge += 1

        if nudge:
            i = np.where(secs == td_secs)[0][0]
            if nudge > 0:
                i = min(secs.size - 1, i + nudge)
            else:
                i = max(0, i + nudge)
            td_secs = secs[i]

        return bins[td_secs]["locator"], bins[td_secs]["formatter"]

    return get_locator_and_formatter


def get_major_locator_and_formatter(
    x_min: np.datetime64,
    x_max: np.datetime64,
    width: float,
    tz: Timezone,
    nudge: int = 0,
):
    get_locator_and_formatter = make_get_locator_and_formatter(tz=tz)
    secs_per_inch = (x_max - x_min).astype("timedelta64[s]").astype(
        np.int64
    ) / width
    return get_locator_and_formatter(secs_per_inch=secs_per_inch, nudge=nudge)

from typing import Mapping
from typing import Any

from matplotlib.axes import Axes
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.dates import date2num
import numpy as np
from fintime.types import Ohlc

from fintime.artists.utils import (
    get_rectangle_vertices,
    get_horizontal_line_segments,
    get_vertical_line_segments,
    to_num_td,
)
from fintime.abc import Artist


class CandleStick(Artist):
    def __init__(
        self, data: Ohlc = {}, twinx: bool = False, config: Mapping[str, Any] = {}
    ):
        self._data = data
        self._twinx = twinx
        self._cfg = config

    def get_width(self) -> float:
        if self._cfg.candlestick.panel.width:
            return self._cfg.candlestick.panel.width
        return self._cfg.candlestick.panel.width_per_bar * self._data["dt"].size

    def get_height(self) -> float:
        return self._cfg.candlestick.panel.height

    def get_xmin(self) -> np.datetime64:
        return self._data["dt"][0]

    def get_xmax(self) -> np.datetime64:
        td = self._data["dt"][-1] - self._data["dt"][-2]
        return self._data["dt"][-1] + td

    def get_ymin(self) -> float:
        padding = self._cfg.candlestick.padding.ymin
        delta = max(self._data["high"]) - min(self._data["low"])
        return min(self._data["low"]) - delta * padding

    def get_ymax(self) -> float:
        padding = self._cfg.candlestick.padding.ymax
        delta = max(self._data["high"]) - min(self._data["low"])
        ymax = max(self._data["high"]) + delta * padding
        return ymax

    def draw(self, axes: Axes) -> Axes:
        b_xmin = date2num(self._data["dt"])
        b_num_td = to_num_td(self._data["dt"])
        b_open = self._data["open"]
        b_high = self._data["high"]
        b_low = self._data["low"]
        b_close = self._data["close"]

        b_xmax = b_xmin + b_num_td * self._cfg.candlestick.body.relwidth
        b_ymin = np.minimum(b_open, b_close)
        b_ymax = np.maximum(b_open, b_close)

        indices_with_doji = np.where(b_open == b_close)[0]
        indices_without_doji = np.where(b_open != b_close)[0]

        body_verts = get_rectangle_vertices(
            b_xmin=b_xmin[indices_without_doji],
            b_xmax=b_xmax[indices_without_doji],
            b_ymin=b_ymin[indices_without_doji],
            b_ymax=b_ymax[indices_without_doji],
        )

        doji_segs = get_horizontal_line_segments(
            b_xmin=b_xmin[indices_with_doji],
            b_xmax=b_xmax[indices_with_doji],
            b_y=b_ymin[indices_with_doji],
        )

        b_x = (b_xmin + b_xmax) * 0.5
        indices_with_upper_wick = np.where(b_ymin != b_low)[0]
        indices_with_lower_wick = np.where(b_ymax != b_high)[0]

        upper_wick_segs = get_vertical_line_segments(
            b_x=b_x[indices_with_upper_wick],
            b_ymin=b_low[indices_with_upper_wick],
            b_ymax=b_ymin[indices_with_upper_wick],
        )
        lower_wick_segs = get_vertical_line_segments(
            b_x=b_x[indices_with_lower_wick],
            b_ymin=b_ymax[indices_with_lower_wick],
            b_ymax=b_high[indices_with_lower_wick],
        )

        wick_segs = np.concatenate((upper_wick_segs, lower_wick_segs), axis=0)

        facecolors = np.where(
            b_close[indices_without_doji] >= b_open[indices_without_doji],
            self._cfg.candlestick.body.up_color,
            self._cfg.candlestick.body.down_color,
        )

        bodies = PolyCollection(
            verts=body_verts,
            facecolors=facecolors,
            zorder=self._cfg.candlestick.zorder,
            alpha=self._cfg.candlestick.body.alpha,
        )

        wicks = LineCollection(
            segments=wick_segs,
            colors=self._cfg.candlestick.wick.color,
            linewidths=self._cfg.candlestick.wick.linewidth,
            zorder=self._cfg.candlestick.zorder,
        )

        dojis = LineCollection(
            segments=doji_segs,
            colors=self._cfg.candlestick.wick.color,
            linewidths=self._cfg.candlestick.doji.linewidth,
            zorder=self._cfg.candlestick.zorder,
        )
        axes.add_artist(bodies)
        axes.add_artist(wicks)
        axes.add_artist(dojis)

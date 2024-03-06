from typing import Mapping
from typing import Any

from matplotlib.axes import Axes
from matplotlib.collections import PolyCollection
from matplotlib.dates import date2num
import numpy as np

from fintime.abc import Artist
from fintime.types import Volume
from fintime.artists.utils import get_rectangle_vertices, to_num_td


class Volume(Artist):
    def __init__(
        self,
        data: Volume = {},
        twinx: bool = False,
        config: Mapping[str, Any] = {},
    ):
        self._data = data
        self._twinx = twinx
        self._cfg = config

    def get_width(self) -> float:
        if self._cfg.volume.panel.width:
            return self._cfg.volume.panel.width
        return self._cfg.volume.panel.width_per_bar * self._data["dt"].size

    def get_height(self) -> float:
        return self._cfg.volume.panel.height

    def get_xmin(self) -> np.datetime64:
        return self._data["dt"][0]

    def get_xmax(self) -> float:
        td = self._data["dt"][-1] - self._data["dt"][-2]
        return self._data["dt"][-1] + td

    def get_ymin(self) -> float:
        return 0.0

    def get_ymax(self) -> float:
        max_vol = max(self._data["vol"])
        return max_vol + max_vol * self._cfg.volume.padding.ymax

    def draw(self, axes: Axes) -> Axes:
        b_xmin = date2num(self._data["dt"])
        b_num_td = to_num_td(self._data["dt"])
        b_vol = self._data["vol"]
        b_close = self._data["close"]
        b_close_last = np.roll(b_close, 1)

        b_xmax = b_xmin + b_num_td * self._cfg.candlestick.body.relwidth
        b_ymin = np.zeros_like(b_vol)
        b_ymax = b_vol

        indices_with_volume = np.where(b_ymax)[0]

        body_verts = get_rectangle_vertices(
            b_xmin=b_xmin[indices_with_volume],
            b_xmax=b_xmax[indices_with_volume],
            b_ymin=b_ymin[indices_with_volume],
            b_ymax=b_ymax[indices_with_volume],
        )

        price_diff = b_close - b_close_last
        c_up = np.where(price_diff > 0, self._cfg.volume.facecolor.up, "")
        c_down = np.where(price_diff < 0, self._cfg.volume.facecolor.down, "")
        c_flat = np.where(price_diff == 0, self._cfg.volume.facecolor.flat, "")
        facecolors = np.char.add(np.char.add(c_up, c_down), c_flat)
        facecolors[0] = self._cfg.volume.facecolor.flat

        bodies = PolyCollection(
            verts=body_verts,
            facecolors=facecolors,
            zorder=self._cfg.candlestick.zorder,
            alpha=self._cfg.candlestick.body.alpha,
        )

        axes.add_artist(bodies)

        return axes

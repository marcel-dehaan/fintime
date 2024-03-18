from typing import Any, Mapping, Optional

import numpy as np
from matplotlib.axes import Axes
from matplotlib.collections import LineCollection

from fintime.abc import Artist
from fintime.utils import safe_cast_dt64, infer_yfeat
from fintime.validation import check_key_presence
from fintime.artists.utils import get_rolled_line_segments


class Line(Artist):
    def __init__(
        self,
        data: Optional[Mapping[str, Any]] = None,
        config: Optional[Mapping[str, Any]] = None,
        twinx: bool = False,
        *,
        xfeat: str = "dt",
        yfeat: Optional[str] = None,
        ylabel: Optional[str] = None
    ):
        super().__init__(data=data, config=config, twinx=twinx)
        self._xfeat = xfeat
        self._yfeat = yfeat
        self._ylabel = ylabel

    def validate(self):
        check_key_presence(self._xfeat, self._data, self.__class__.__name__)

        if self._yfeat is None:
            self._yfeat = infer_yfeat(data=self._data, xfeat=self._xfeat)

    def get_width(self) -> float:
        return min(
            len(self._data[self._xfeat])
            * self._cfg.line.panel.width_per_data_point,
            self._cfg.line.panel.max_width,
        )

    def get_ylabel(self) -> str:
        return self._ylabel

    def get_height(self) -> float:
        return self._cfg.line.panel.height

    def get_xmin(self) -> np.datetime64:
        return self._data[self._xfeat][0]

    def get_xmax(self) -> np.datetime64:
        return self._data[self._xfeat][-1]

    def get_ymin(self) -> float:
        padding = self._cfg.line.padding.ymax
        delta = max(self._data[self._yfeat]) - min(self._data[self._yfeat])
        return min(self._data[self._yfeat]) - delta * padding

    def get_ymax(self) -> float:
        padding = self._cfg.line.padding.ymax
        delta = max(self._data[self._yfeat]) - min(self._data[self._yfeat])
        return max(self._data[self._yfeat]) + delta * padding

    def draw(self, axes: Axes) -> None:
        self.validate()
        b_x = safe_cast_dt64(self._data[self._xfeat])
        b_y = self._data[self._yfeat]
        segs = get_rolled_line_segments(b_x, b_y)

        line_collection = LineCollection(
            segs,
            colors=self._cfg.line.color,
            linewidths=self._cfg.line.linewidth,
            zorder=self._cfg.line.zorder,
            linestyle=self._cfg.line.linestyle,
            label="hi",
        )

        axes.add_artist(line_collection)

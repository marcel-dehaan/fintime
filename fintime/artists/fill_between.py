from typing import Any, Mapping, Optional

import numpy as np
from matplotlib.axes import Axes
from matplotlib.dates import date2num

from fintime.abc import Artist
from fintime.types import Fill


class FillBetween(Artist):
    def __init__(
        self,
        data: Optional[Fill] = None,
        config: Optional[Mapping[str, Any]] = None,
        *,
        y1_feat: Optional[str] = None,
        y2_feat: Optional[str] = None,
        twinx: bool = False,
        ylabel: Optional["str"] = None,
    ):
        super().__init__(data, config, twinx)
        if ylabel:
            self._cfg["volume.ylabel"] = ylabel
        self._y1_feat = y1_feat
        self._y2_feat = y2_feat

    def get_width(self) -> float:
        return 5

    def get_height(self) -> float:
        return self._cfg.fill_between.panel.height

    def get_ylabel(self) -> Optional[str]:
        return self._cfg.fill_between.ylabel

    def get_xmin(self) -> np.datetime64:
        return self._data["dt"][0]

    def _get_yrange(self):
        ymin_feat = self._y1_feat if self._y1_feat else self._y2_feat
        ymax_feat = self._y2_feat if self._y2_feat else self._y1_feat
        ymin = min(self._data[ymin_feat])
        ymax = max(self._data[ymax_feat])
        return ymin, ymax

    def get_xmax(self) -> np.datetime64:
        td = self._data["dt"][-1] - self._data["dt"][-2]
        return self._data["dt"][-1] + td

    def get_ymin(self) -> float:
        ymin, ymax = self._get_yrange()
        return (
            ymin - (ymax - ymin) * self._cfg.fill_between.panel.padding.ymin
        )

    def get_ymax(self) -> float:
        ymin, ymax = self._get_yrange()
        return (
            ymax + (ymax - ymin) * self._cfg.fill_between.panel.padding.ymax
        )

    def validate(self) -> None:
        pass

    def draw(self, axes: Axes) -> None:
        b_x = date2num(self._data["dt"])

        if self._y1_feat:
            b_y1 = self._data[self._y1_feat]
        else:
            b_y1 = np.full_like(
                self._data[self._y2_feat], fill_value=self._ymin
            )
        if self._y2_feat:
            b_y2 = self._data[self._y2_feat]
        else:
            b_y2 = np.full_like(
                self._data[self._y1_feat], fill_value=self._ymax
            )

        axes.fill_between(
            b_x,
            b_y1,
            b_y2,
            color=self._cfg.fill_between.face.color,
            alpha=self._cfg.fill_between.alpha,
            edgecolor=self._cfg.fill_between.edge.color,
            linewidth=self._cfg.fill_between.edge.linewidth,
        )

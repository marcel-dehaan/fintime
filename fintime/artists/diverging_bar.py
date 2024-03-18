from typing import Any, Mapping, Optional

from matplotlib.axes import Axes
from matplotlib.dates import date2num
from matplotlib.collections import PolyCollection
import numpy as np

from fintime.abc import Artist
from fintime.validation import check_key_presence
from fintime.utils import infer_yfeat
from fintime.artists.utils import get_rectangle_vertices, to_num_td
from fintime.types import NumberArray1D


class DivergingBar(Artist):
    def __init__(
        self,
        data: Optional[Mapping[str, NumberArray1D]] = None,
        config: Optional[Mapping[str, Any]] = None,
        *,
        feat: str,
        pivot: float = 0.0,
        twinx: bool = False,
        ylabel: Optional["str"] = None,
    ):
        super().__init__(data, config, twinx)
        if ylabel:
            self._cfg["diverging_bar.ylabel"] = ylabel
        self._feat = feat
        self._pivot = pivot

    def get_width(self) -> float:
        return (
            self._cfg.diverging_bar.panel.width
            if self._cfg.diverging_bar.panel.width
            else self._cfg.diverging_bar.panel.width_per_bar
            * self._data["dt"].size
        )

    def get_height(self) -> float:
        return self._cfg.diverging_bar.panel.height

    def get_xmin(self) -> np.datetime64:
        return self._data["dt"][0]

    def get_xmax(self) -> np.datetime64:
        td = self._data["dt"][-1] - self._data["dt"][-2]
        return self._data["dt"][-1] + td

    def get_ymin(self) -> float:
        return (
            min(self._data[self._feat])
            - (max(self._data[self._feat]) - min(self._data[self._feat]))
            * self._cfg.diverging_bar.panel.padding.ymin
        )

    def get_ymax(self) -> float:
        return (
            max(self._data[self._feat])
            + (max(self._data[self._feat]) - min(self._data[self._feat]))
            * self._cfg.diverging_bar.panel.padding.ymin
        )

    def get_ylabel(self) -> str:
        return self._cfg.diverging_bar.panel.ylabel or self._feat

    def validate(self):
        check_key_presence(self._feat, self._data, self.__class__.__name__)

        if self._feat is None:
            self._feat = infer_yfeat(data=self._data, xfeat=self._feat)

    def draw(self, axes: Axes) -> None:
        print("here")
        b_xmin = date2num(self._data["dt"])
        b_num_td = to_num_td(self._data["dt"])

        b_xmax = b_xmin + b_num_td * self._cfg.diverging_bar.relwidth

        b_feat = self._data[self._feat]
        b_pivot = np.full_like(b_feat, self._pivot)

        verts = get_rectangle_vertices(
            b_xmin=b_xmin, b_xmax=b_xmax, b_ymin=b_feat, b_ymax=b_pivot
        )

        p_abs = b_feat - b_pivot
        c_up = np.where(p_abs > 0, self._cfg.diverging_bar.face.color.up, "")
        c_down = np.where(
            p_abs < 0, self._cfg.diverging_bar.face.color.down, ""
        )
        facecolors = np.char.add(c_up, c_down)

        p_abs = b_feat - b_pivot
        c_up = np.where(p_abs > 0, self._cfg.diverging_bar.edge.color.up, "")
        c_down = np.where(
            p_abs < 0, self._cfg.diverging_bar.edge.color.down, ""
        )
        edgecolors = np.char.add(c_up, c_down)

        poly_collection = PolyCollection(
            verts,
            facecolors=facecolors,
            edgecolors=edgecolors,
            zorder=10,
            alpha=1,
        )

        axes.add_artist(poly_collection)

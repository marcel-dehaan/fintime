from typing import Any, Mapping, Optional

import numpy as np
from matplotlib.axes import Axes
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.dates import date2num

from fintime.abc import Artist
from fintime.types import Volume
from fintime.artists.utils import (
    get_horizontal_line_segments,
    get_rectangle_vertices,
    get_vertical_line_segments,
    to_num_td,
)
from fintime.validation import validate


class Volume(Artist):
    def __init__(
        self,
        data: Optional[Volume] = None,
        config: Optional[Mapping[str, Any]] = None,
        twinx: bool = False,
        *,
        ylabel: Optional["str"] = None,
    ):
        super().__init__(data, config, twinx)
        if ylabel:
            self._cfg["volume.ylabel"] = ylabel

    def get_width(self) -> float:
        return (
            self._cfg.volume.panel.width
            if self._cfg.volume.panel.width
            else self._cfg.volume.panel.width_per_bar * len(self._data["dt"])
        )

    def get_ylabel(self) -> str:
        return self._cfg.volume.ylabel

    def get_height(self) -> float:
        return self._cfg.volume.panel.height

    def get_xmin(self) -> np.datetime64:
        return self._data["dt"][0]

    def get_xmax(self) -> np.datetime64:
        td = self._data["dt"][-1] - self._data["dt"][-2]
        return self._data["dt"][-1] + td

    def get_ymin(self) -> float:
        return 0.0

    def get_ymax(self) -> float:
        max_vol = max(self._data["vol"])
        return max_vol + max_vol * self._cfg.volume.padding.ymax

    def validate(self) -> None:
        validate(
            data=self._data,
            data_type_mapping=self._cfg.volume.data.types,
            class_name=self.__class__.__name__,
        )

    def draw(self, axes: Axes) -> None:
        b_xmin = date2num(self._data["dt"])
        b_num_td = to_num_td(self._data["dt"])
        b_vol = self._data["vol"]
        b_close = self._data["close"]
        b_close_last = np.roll(b_close, 1)

        b_xmax = b_xmin + b_num_td * self._cfg.volume.relwidth
        b_ymin = np.zeros_like(b_vol)
        b_ymax = b_vol

        indices_with_volume = np.where(b_ymax)[0]

        face_verts = get_rectangle_vertices(
            b_xmin=b_xmin[indices_with_volume],
            b_xmax=b_xmax[indices_with_volume],
            b_ymin=b_ymin[indices_with_volume],
            b_ymax=b_ymax[indices_with_volume],
        )

        price_diff = b_close - b_close_last
        c_up = np.where(price_diff > 0, self._cfg.volume.face.color.up, "")
        c_down = np.where(
            price_diff < 0, self._cfg.volume.face.color.down, ""
        )
        c_flat = np.where(
            price_diff == 0, self._cfg.volume.face.color.flat, ""
        )
        facecolors = np.char.add(np.char.add(c_up, c_down), c_flat)
        facecolors[0] = self._cfg.volume.face.color.flat

        faces = PolyCollection(
            verts=face_verts,
            facecolors=facecolors,
            zorder=self._cfg.volume.zorder,
            alpha=self._cfg.volume.face.alpha,
        )
        axes.add_artist(faces)

        # Don't waste compute cycles drawing non-visible edges.
        if self._cfg.volume.edge.linewidth and self._cfg.volume.edge.alpha:

            segs0 = get_vertical_line_segments(
                b_x=b_xmin[indices_with_volume],
                b_ymin=b_ymin[indices_with_volume],
                b_ymax=b_ymax[indices_with_volume],
            )

            segs1 = get_vertical_line_segments(
                b_x=b_xmax[indices_with_volume],
                b_ymin=b_ymin[indices_with_volume],
                b_ymax=b_ymax[indices_with_volume],
            )
            segs2 = get_horizontal_line_segments(
                b_xmin=b_xmin[indices_with_volume],
                b_xmax=b_xmax[indices_with_volume],
                b_y=b_ymax[indices_with_volume],
            )
            c_up = np.where(
                price_diff > 0, self._cfg.volume.edge.color.up, ""
            )
            c_down = np.where(
                price_diff < 0, self._cfg.volume.edge.color.down, ""
            )
            c_flat = np.where(
                price_diff == 0, self._cfg.volume.edge.color.flat, ""
            )
            edgecolors = np.char.add(np.char.add(c_up, c_down), c_flat)
            edgecolors[0] = self._cfg.volume.edge.color.flat

            for segs in [segs0, segs1, segs2]:
                edges = LineCollection(
                    segments=segs,
                    colors=edgecolors,
                    linewidths=self._cfg.volume.edge.linewidth,
                    zorder=self._cfg.volume.zorder,
                    alpha=self._cfg.volume.edge.alpha,
                    capstyle=None,
                )

                axes.add_artist(edges)

        return axes

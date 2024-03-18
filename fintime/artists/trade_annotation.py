from typing import Any, Mapping, Optional

import numpy as np
from matplotlib.axes import Axes
from matplotlib.dates import date2num

from fintime.abc import Artist
from fintime.types import Fill
from fintime.validation import validate


class TradeAnnotation(Artist):
    def __init__(
        self,
        data: Optional[Fill] = None,
        config: Optional[Mapping[str, Any]] = None,
        *,
        twinx: bool = False,
        ylabel: Optional["str"] = None,
    ):
        super().__init__(data, config, twinx)
        if ylabel:
            self._cfg["trade_annotation.panel.ylabel"] = ylabel
        self._ymin = None
        self._ymax = None

    def get_width(self) -> float:
        return self._cfg.trade_annotation.panel.width

    def get_height(self) -> float:
        return self._cfg.trade_annotation.panel.height

    def get_xmin(self) -> np.datetime64:
        return self._data["dt"][0]

    def get_xmax(self) -> np.datetime64:
        return self._data["dt"][-1]

    def get_ymin(self) -> float:
        arr = self._data["price"]
        return self._ymin or arr[arr != 0].min()

    def get_ymax(self) -> float:
        arr = self._data["price"]
        return self._ymax or arr[arr != 0].max()

    def get_ylabel(self) -> str:
        return self._cfg.trade_annotation.panel.ylabel

    def validate(self):
        validate(
            data=self._data,
            data_type_mapping=self._cfg.trade_annotation.data.types,
            class_name=self.__class__.__name__,
        )

    def draw(self, axes: Axes) -> None:

        iterations = 3

        for i in range(iterations):

            indx_fills = np.where(self._data["size"] != 0)[0]
            b_num_dt = date2num(self._data["dt"])

            b_x = b_num_dt[indx_fills]
            b_price = self._data["price"][indx_fills]
            b_size = self._data["size"][indx_fills]
            b_side = self._data["side"][indx_fills]

            xmin_axes, xmax_axes = axes.get_xlim()
            ymin_axes, ymax_axes = axes.get_ylim()

            x_range = abs(xmax_axes - xmin_axes)
            y_range = abs(ymax_axes - ymin_axes)

            x_range_per_inch = x_range / self._width
            y_range_per_inch = y_range / self._height

            x_span_char = x_range_per_inch / 4.5
            y_span_bbox = y_range_per_inch / 2.4

            get_text = self._cfg.trade_annotation.fn_annotation

            fills = []
            for x, price, size, side in zip(b_x, b_price, b_size, b_side):
                xmax = x

                vside = self._cfg.trade_annotation.vside[side]

                text = get_text(price=price, size=size, side=side)
                xmin = xmax - x_span_char * len(text)

                if xmin < xmin_axes:
                    xmin = xmax
                    xmax = xmin + x_span_char * len(text)
                    halign = "left"
                else:
                    halign = "right"

                i_start = np.searchsorted(b_num_dt, xmin, side="left")
                i_stop = np.searchsorted(b_num_dt, xmax, side="right")

                sl = slice(i_start, i_stop)

                if vside == "top":
                    valign = "bottom"
                    ymin = self._data["high"][sl].max() + 0.03 * y_range
                    ymax = ymin + y_span_bbox

                else:
                    valign = "top"
                    ymax = self._data["low"][sl].min() - 0.03 * y_range
                    ymin = ymax - y_span_bbox

                for _xmin, _xmax, _ymin, _ymax, *_ in fills:
                    collision = not (
                        xmax < _xmin
                        or _xmax < xmin
                        or ymax < _ymin
                        or _ymax < ymin
                    )
                    if collision:
                        if vside == "top":
                            ymin = _ymax
                            ymax = ymin + y_span_bbox
                        else:
                            ymax = _ymin
                            ymin = ymax - y_span_bbox

                fills.append((xmin, xmax, ymin, ymax, halign, valign, text))

            if i < iterations - 1:
                ymax = max([f[3] for f in fills])
                ymin = min([f[2] for f in fills])
                ymin_axes, y_max_axes = axes.get_ylim()
                if ymax > y_max_axes:
                    y_max_axes = ymax + y_span_bbox
                    axes.set_ylim(ymin_axes, y_max_axes)

                if ymin < ymin_axes:
                    ymin_axes = ymin - y_span_bbox * 4
                    axes.set_ylim(ymin_axes, y_max_axes)

        for (
            xmax,
            price,
            size,
            side,
            (xmin, _xmax, ymin, ymax, halign, valign, text),
        ) in zip(b_x, b_price, b_size, b_side, fills):
            axes.annotate(
                "",
                xy=(xmax, price),
                xytext=(xmax, ymin),
                zorder=109,
                arrowprops=dict(
                    facecolor=self._cfg.trade_annotation.arrow.face.color[
                        side
                    ],
                    edgecolor=self._cfg.trade_annotation.arrow.edge.color[
                        side
                    ],
                    linewidth=self._cfg.trade_annotation.arrow.edge.linewidth,
                    width=self._cfg.trade_annotation.arrow.width,
                    headwidth=self._cfg.trade_annotation.arrow.headwidth,
                    headlength=self._cfg.trade_annotation.arrow.headlength,
                ),
            )

            axes.text(
                x=xmax,
                y=ymin,
                s=text,
                color=self._cfg.trade_annotation.text.color,
                zorder=110,
                horizontalalignment=halign,
                verticalalignment=valign,
                fontdict=dict(
                    family=self._cfg.trade_annotation.text.font.family,
                    size=self._cfg.trade_annotation.text.font.size,
                    weight=self._cfg.trade_annotation.text.font.weigth,
                ),
                bbox=dict(
                    boxstyle=self._cfg.trade_annotation.text.bbox.boxstyle,
                    facecolor=self._cfg.trade_annotation.text.bbox.face.color[
                        side
                    ],
                    edgecolor=self._cfg.trade_annotation.text.bbox.edge.color[
                        side
                    ],
                    linewidth=self._cfg.trade_annotation.text.bbox.edge.linewidth,
                    alpha=self._cfg.trade_annotation.text.bbox.alpha,
                ),
            )

from typing import Any, Mapping

import numpy as np
from matplotlib.axes import Axes
from matplotlib.dates import date2num
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec, SubplotSpec, GridSpecFromSubplotSpec

from fintime.abc import Composite, Artist, XLim, YLim
from fintime.config import Config
from fintime.ticks import get_major_locator_and_formatter
from fintime.types import SizeSpec


class Panel(Composite, XLim, YLim):
    def __init__(
        self,
        artists: list[Artist],
        data: dict = {},
        size: SizeSpec = (None, None),
        config: Mapping[str, Any] = {},
    ):
        super().__init__(
            components=artists,
            width=size[0],
            height=size[1],
            op_widths=max,
            op_heights=max,
        )
        self._artists = artists
        self._cfg = Config(config)
        self._data = data

    def get_xmin(self) -> float:
        return min([comp.get_xmin() for comp in self._components])

    def get_xmax(self) -> float:
        return min([comp.get_xmax() for comp in self._components])

    def get_ymin(self, twinx: bool = False) -> float:
        return min(
            [
                artist.get_ymin()
                for artist in self._components
                if artist.is_twinx() == twinx
            ]
        )

    def get_ylabel(self, twinx: bool = False):
        labels = [
            artist.get_ylabel()
            for artist in self._components
            if artist.is_twinx() == twinx
        ]
        labels = [label for label in labels if label]
        if not labels:
            return None
        if not all(item == labels[0] for item in labels):
            raise ValueError(
                f"Panel encountered non-identical ylabels: {labels}. "
            )
        return labels[0]

    def get_ymax(self, twinx: bool = False) -> float:
        return max(
            [
                comp.get_ymax()
                for comp in self._components
                if comp.is_twinx() == twinx
            ]
        )

    def set_xlim(self, xmin, xmax):
        self._xmin = xmin
        self._xmax = xmax

    def draw(self, axes: Axes) -> None:

        axes.set_facecolor(self._cfg.panel.facecolor)
        all_axes = {False: axes}
        if any([artist.is_twinx() for artist in self._artists]):
            all_axes[True] = axes.twinx()
        else:
            axes.yaxis.set_tick_params(right=True, labelright=True)

        for twinx, axes in all_axes.items():
            ylim = (self.get_ymin(twinx), self.get_ymax(twinx))

            all_axes[twinx].set_ylim(*ylim)
            all_axes[twinx].set_ylabel(
                self.get_ylabel(twinx),
                fontdict={
                    "family": self._cfg.ylabel.font.family,
                    "color": self._cfg.ylabel.font.color,
                    "weight": self._cfg.ylabel.font.weight,
                    "size": self._cfg.ylabel.font.size,
                },
                labelpad=self._cfg.ylabel.pad,
            )

        for artist in self._artists:
            twinx = artist.is_twinx()
            artist.set_ylim(self.get_ymin(twinx), self.get_ymax(twinx))
            artist.set_xlim(self._xmin, self._xmax)
            artist.draw(all_axes[twinx])


class Subplot(Composite, XLim):
    def __init__(
        self,
        panels: list[Panel],
        data: dict = {},
        size: SizeSpec = (None, None),
        config: Mapping[str, Any] = {},
    ):
        super().__init__(
            components=panels,
            width=size[0],
            height=size[1],
            op_widths=max,
            op_heights=sum,
        )
        self._cfg = Config(config)
        self._data = data

    def get_xmin(self) -> float:
        return min([comp.get_xmin() for comp in self._components])

    def get_xmax(self) -> float:
        return min([comp.get_xmax() for comp in self._components])

    def get_ymin(self) -> float:
        return min([comp.get_ymin() for comp in self._components])

    def get_ymax(self) -> float:
        return max([comp.get_ymax() for comp in self._components])

    def draw(self, canvas: Figure | SubplotSpec) -> None:

        if isinstance(canvas, SubplotSpec):

            gs = GridSpecFromSubplotSpec(
                nrows=self.nrows,
                ncols=1,
                subplot_spec=canvas,
                height_ratios=self._get_heights(),
                hspace=0.0,
                wspace=0,
            )
        else:
            gs = GridSpec(
                nrows=self.nrows,
                ncols=1,
                height_ratios=self._get_heights(),
                figure=canvas,
                hspace=0,
                wspace=0.01,
            )

        xmin = self.get_xmin()
        xmax = self.get_xmax()

        locator, formatter = get_major_locator_and_formatter(
            x_min=xmin,
            x_max=xmax,
            width=self.get_width(),
            nudge=self._cfg.panel.xaxis.tick.nudge,
            tz=self._cfg.timezone,
        )
        if isinstance(xmin, np.datetime64):
            xmin = date2num(xmin)
            xmax = date2num(xmax)

        nrows, ncols = gs.get_geometry()
        axes_list = gs.subplots()
        if isinstance(axes_list, Axes):
            axes_list = [axes_list]

        for panel, axes in zip(self._components, axes_list):

            rowspan = axes.get_subplotspec().rowspan
            labeltop = rowspan.start == 0
            labelbottom = rowspan.stop == nrows
            axes.set_xlim(xmin, xmax)
            axes.grid(
                linestyle=self._cfg.grid.linestyle,
                alpha=self._cfg.grid.alpha,
                zorder=self._cfg.grid.zorder,
                linewidth=self._cfg.grid.linewidth,
                color=self._cfg.grid.color,
            )
            axes.tick_params(
                which="both",
                labelsize=12,
                top=labeltop,
                bottom=labelbottom,
                right=True,
            )
            axes.xaxis.set_tick_params(
                labeltop=labeltop, labelbottom=labelbottom, direction="out"
            )
            axes.xaxis.set_major_locator(locator=locator)
            axes.xaxis.set_major_formatter(formatter=formatter)
            panel.set_xlim(xmin, xmax)

            panel.draw(axes)

        # enforce x-axis panel alignment when interatively viewed.
        for i in range(1, len(axes_list)):
            axes_list[i].sharex(axes_list[i - 1])


class Grid(Composite):
    def __init__(
        self,
        subplots: list[Subplot],
        size: SizeSpec,
        data,
        config,
    ):
        super().__init__(
            components=subplots,
            width=size[0],
            height=size[1],
            op_widths=max,
            op_heights=sum,
        )

        self._data = data
        self._cfg = config

    def draw(self, canvas) -> None:
        # TODO: improve dynamic hspace logic
        gridspec = GridSpec(
            nrows=self.nrows,
            ncols=1,
            height_ratios=self._get_heights(),
            figure=canvas,
            hspace=4 / self._height + 0.05,
            wspace=0,
        )
        for subplot, subplot_spec in zip(self._components, gridspec):
            subplot.draw(canvas=subplot_spec)

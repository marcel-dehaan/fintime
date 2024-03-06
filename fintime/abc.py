from typing import Optional, Callable, Any, Mapping
from abc import ABC, abstractmethod
from copy import deepcopy

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.gridspec import SubplotSpec
from fieldconfig import Config


class XLim(ABC):
    """
    Specifies the shared x-axis for Artists, Panels, and Subplots.
    """

    @abstractmethod
    def get_xmin(self) -> float: ...

    @abstractmethod
    def get_xmax(self) -> float: ...


class YLim(ABC):
    """
    Specifies the shared y-axis for Artists and Panels.
    """

    @abstractmethod
    def get_ymin(self, twinx: bool = False) -> float: ...

    @abstractmethod
    def get_ymax(self, twinx: bool = False) -> float: ...


class Sized(ABC):
    """
    Specifies the shared protocol for Artists, Panels, Subplots, and Grid.
    """

    @abstractmethod
    def get_width(self) -> float:
        """Return width in inches."""

    @abstractmethod
    def get_height(self) -> float:
        """Return height in inches."""

    @abstractmethod
    def draw(self, canvas: Figure | SubplotSpec | Axes) -> None:
        """Draw the component on the specified canvas."""

    def _set_size(self, width: float, height: float) -> None:
        """Set the components width and height in inches"""

        self._width = width
        self._height = height

    def _update_data(self, data: Mapping[str, Any]):
        """Update the inherited data with local updates, if any are present."""

        data.update(self._data)
        self._data = data

    def _update_config(self, config: Config):
        """Update the inherited Config with local updates, if any are present."""

        config.update(self._cfg)
        self._cfg = config


class Artist(Sized, XLim, YLim):
    def is_twinx(self):
        return self._twinx

    def propagate_data(self, data: Mapping[str, Any]) -> None:
        self._update_data(data=data)

    def propagate_config(self, config: Config) -> None:
        self._update_config(config=config)

    def propagate_size(self, width: float, height: float) -> None:
        self._set_size(width=width, height=height)


class Composite(Sized):
    def __init__(
        self,
        components: list[Sized],
        width: Optional[float],
        height: Optional[float],
        op_heights: Callable[[float], float],
        op_widths: Callable[[float], float],
    ):
        self._components = components
        self._width = width
        self._height = height
        self._op_widths = op_widths
        self._op_heights = op_heights

    @property
    def nrows(self):
        return len(self._components)

    def _get_heights(self) -> list[float]:
        return [comp.get_height() for comp in self._components]

    def _get_widths(self) -> list[float]:
        return [comp.get_width() for comp in self._components]

    def get_height(self) -> float:
        if self._height:
            return self._height
        return self._op_heights(self._get_heights())

    def get_width(self) -> float:
        if self._width:
            return self._width
        return self._op_widths(self._get_widths())

    def propagate_data(self, data: Mapping[str, Any]) -> None:
        self._update_data(data=data)

        for comp in self._components:
            comp.propagate_data(data=deepcopy(data))

    def propagate_config(self, config: Config) -> None:
        self._update_config(config=config)

        for comp in self._components:
            comp.propagate_config(config=config.copy())

    def propagate_size(self, width: float, height: float) -> None:
        self._set_size(width=width, height=height)

        old_height = self.get_height()
        scalar = height / old_height
        new_heights = [h * scalar for h in self._get_heights()]

        for comp, new_height in zip(self._components, new_heights):
            comp.propagate_size(width, new_height)

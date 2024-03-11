from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Callable, Mapping, Optional

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.gridspec import SubplotSpec

from fieldconfig import Config


class XLim(ABC):
    """
    Specifies the shared x-axis for Artists, Panels, and Subplots.
    """

    @abstractmethod
    def get_xmin(self) -> float:
        """Get the minimum value of the x-axis."""
        pass

    @abstractmethod
    def get_xmax(self) -> float:
        """Get the maximum value of the x-axis."""
        pass


class YLim(ABC):
    """
    Specifies the shared y-axis for Artists and Panels.
    """

    @abstractmethod
    def get_ymin(self, twinx: bool = False) -> float:
        """Get the minimum value of the y-axis."""
        pass

    @abstractmethod
    def get_ymax(self, twinx: bool = False) -> float:
        """Get the maximum value of the y-axis."""
        pass


class Sized(ABC):
    """
    Specifies the shared protocol for Artists, Panels, Subplots, and Grid.
    """

    @abstractmethod
    def get_width(self) -> float:
        """
        Return the width of the component in inches.
        """
        pass

    @abstractmethod
    def get_height(self) -> float:
        """
        Return the height of the component in inches.
        """
        pass

    @abstractmethod
    def draw(self, canvas: Figure | SubplotSpec | Axes) -> None:
        """
        Draw the component on the specified canvas.
        """
        pass

    def _set_size(self, width: float, height: float) -> None:
        """
        Set the width and height of the component in inches.

        Parameters:
        - width (float): The width of the component.
        - height (float): The height of the component.
        """
        self._width = width
        self._height = height

    def _update_data(self, data: Mapping[str, Any]) -> None:
        """
        Update the inherited data with local updates, if any are present.

        Parameters:
        - data (Mapping[str, Any]): Local updates to the data.
        """
        data.update(self._data)
        self._data = data

    def _update_config(self, config: Config) -> None:
        """
        Update the inherited Config with local updates, if any are present.

        Parameters:
        - config (Config): Local updates to the configuration.
        """
        config.update(self._cfg)
        self._cfg = config


class Artist(Sized, XLim, YLim):
    """
    Base class for Artists, implementing common functionality.
    """

    def __init__(
        self,
        data: Optional[Mapping[str, Any]],
        config: Optional[Mapping[str, Any]],
        twinx: bool,
    ):
        self._data = data or {}
        self._cfg = config or {}
        self._twinx = twinx

    def is_twinx(self):
        """Check if the artist is twinx."""
        return self._twinx

    def get_ylabel(self) -> Optional[str]:
        """Get the ylabel of the artist."""
        return None

    def propagate_data(self, data: Mapping[str, Any]) -> None:
        """Propagate data updates to the artist."""
        self._update_data(data=data)

    def propagate_config(self, config: Config) -> None:
        """Propagate config updates to the artist."""
        self._update_config(config=config)

    def propagate_size(self, width: float, height: float) -> None:
        """Propagate size updates to the artist."""
        self._set_size(width=width, height=height)

    @abstractmethod
    def validate(self):
        """Validate the artist."""
        pass


class Composite(Sized):
    """
    A composite class that groups multiple components.
    """

    def __init__(
        self,
        components: list[Sized],
        width: Optional[float],
        height: Optional[float],
        op_heights: Callable[[list[float]], float],
        op_widths: Callable[[list[float]], float],
    ):
        self._components = components
        self._width = width
        self._height = height
        self._op_widths = op_widths
        self._op_heights = op_heights

    @property
    def nrows(self):
        """Get the number of rows in the composite."""
        return len(self._components)

    def _get_heights(self) -> list[float]:
        """Get the heights of individual components."""
        return [comp.get_height() for comp in self._components]

    def _get_widths(self) -> list[float]:
        """Get the widths of individual components."""
        return [comp.get_width() for comp in self._components]

    def get_height(self) -> float:
        """Get the total height of the composite."""
        return self._height or self._op_heights(self._get_heights())

    def get_width(self) -> float:
        """Get the total width of the composite."""
        return self._width or self._op_widths(self._get_widths())

    def propagate_data(self, data: Mapping[str, Any]) -> None:
        """Propagate data updates to the composite and its components."""
        self._update_data(data=data)

        for comp in self._components:
            comp.propagate_data(data=deepcopy(data))

    def propagate_config(self, config: Config) -> None:
        """Propagate config updates to the composite and its components."""
        self._update_config(config=config)

        for comp in self._components:
            comp.propagate_config(config=config.copy())

    def propagate_size(self, width: float, height: float) -> None:
        """Propagate size updates to the composite and its components."""
        self._set_size(width=width, height=height)

        old_height = self.get_height()
        scalar = height / old_height if old_height else 1.0
        new_heights = [h * scalar for h in self._get_heights()]

        for comp, new_height in zip(self._components, new_heights):
            comp.propagate_size(width, new_height)

    def validate(self) -> None:
        """Validate the composite and its components."""
        for comp in self._components:
            comp.validate()

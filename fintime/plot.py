import warnings
from typing import Any, Mapping, Optional

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from fintime.config import get_config
from fintime.types import Array1D, SizeSpec
from fintime.composites import Subplot, Panel, Grid


def plot(
    specs: list[Subplot] | list[Panel],
    data: Mapping[str, Array1D] = {},
    config: Mapping[str, Any] = None,
    *,
    figsize: SizeSpec = (None, None),
    title: Optional[str] = None,
    save: Optional["str"] = None,
    rtn: bool = True,
) -> Optional[Figure]:
    """
    Create a plot using specified subplots or panels.

    Parameters:
    - specs (list[Subplot] | list[Panel]): List of Subplot or Panel instances
    defining the layout of the plot.
    - data (Mapping[str, Array1D], optional): Data to be plotted. Default is an
    empty dictionary.
    - config (Mapping[str, Any], optional): Configuration settings for the plot.
    Default is None.
    - figsize (SizeSpec, optional): Size of the figure. Default is (None, None),
    (size is inferred from subcomponents in specs)
    - title (str, optional): Title for the entire plot. Default is None (no title).
    - save (str, optional): File path to save the plot. Default is None (not saved).
    - rtn (bool, optional): Whether to return the Figure instance. Default is True.

    Returns:
    - Optional[Figure]: The Figure instance if rtn is True, else None.

    Note:
    - Configurations and data are propagated downward to subcomponents, allowing
    for overrides at any level.
    """

    if config is None:
        config = get_config()

    class_name = Subplot if isinstance(specs[0], Panel) else Grid
    gridspec = class_name(specs, size=figsize, data=data, config=config)

    gridspec.propagate_config(config=config)
    gridspec.propagate_data(data=data)

    fig_width = gridspec.get_width()
    fig_height = gridspec.get_height()

    gridspec.propagate_size(width=fig_width, height=fig_height)
    gridspec.validate()

    fig = plt.figure(
        figsize=(fig_width, fig_height),
        layout=config.figure.layout,
        facecolor=config.figure.facecolor,
    )
    if title:
        fig.suptitle(
            title,
            fontfamily=config.figure.title.font.family,
            fontsize=config.figure.title.font.size,
            fontweight=config.figure.title.font.weight,
            y=config.figure.title.y,
        )
    gridspec.draw(canvas=fig)

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="This figure includes Axes that are not compatible with tight_layout",
        )
        if save:
            fig.savefig(save)
    if rtn:
        return fig

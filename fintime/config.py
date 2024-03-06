from typing import Any
from fieldconfig import Config, Field
from dateutil import tz
import matplotlib.colors as mcolors


def is_positive_number(x):
    return x > 0


def is_between_zero_and_one(x):
    return x >= 0 and x <= 1


def is_valid_mpl_color(x):
    try:
        mcolors.to_rgba(x)
        return True
    except ValueError:
        return False


def get_config():

    cfg = Config(create_intermediate_attributes=True)

    cfg.timezone = tz.gettz("America/New_York")
    cfg.figure.layout = "tight"
    cfg.figure.facecolor = "#f9f9f9"

    cfg.figure.title.fontsize = 22
    cfg.figure.title.fontweight = "bold"
    cfg.figure.title.y = Field(0.98, validator=is_between_zero_and_one)

    cfg.panel.facecolor = "white"
    cfg.xaxis.tick.nudge = 0

    cfg.candlestick.panel.height = Field(9.0, validator=is_positive_number)
    cfg.candlestick.panel.width = Field(None, float)
    cfg.candlestick.panel.width_per_bar = 0.1
    cfg.candlestick.padding.ymin = 0.06
    cfg.candlestick.padding.ymax = 0.06
    cfg.candlestick.zorder = 14
    cfg.candlestick.body.relwidth = Field(0.8, validator=is_between_zero_and_one)
    cfg.candlestick.body.alpha = Field(1.0, validator=is_between_zero_and_one)
    cfg.candlestick.body.up_color = Field("#4EA59A", validator=is_valid_mpl_color)
    cfg.candlestick.body.down_color = Field("#E05D57", validator=is_valid_mpl_color)
    cfg.candlestick.wick.color = Field("#000000", validator=is_valid_mpl_color)
    cfg.candlestick.wick.linewidth = 1.0
    cfg.candlestick.wick.alpha = Field(1.0, validator=is_between_zero_and_one)
    cfg.candlestick.doji.color = Field("#000000", validator=is_valid_mpl_color)
    cfg.candlestick.doji.linewidth = 1.0
    cfg.candlestick.doji.alpha = Field(1.0, validator=is_between_zero_and_one)

    cfg.volume.panel.height = Field(3.0, validator=is_positive_number)
    cfg.volume.panel.width = Field(None, ftype=float)
    cfg.volume.padding.ymax = 0.05
    cfg.volume.facecolor.up = Field("#4EA59A", validator=is_valid_mpl_color)
    cfg.volume.facecolor.down = Field("#E05D57", validator=is_valid_mpl_color)
    cfg.volume.facecolor.flat = Field("#b0b0b0", validator=is_valid_mpl_color)
    cfg.volume.panel.width_per_bar = 0.1

    cfg.disable_intermediate_attribute_creation()
    return cfg

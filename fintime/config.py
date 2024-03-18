from dateutil import tz
from matplotlib.pyplot import rcParams

from fieldconfig import Config, Field
from fintime.types import (
    FloatingArray1D,
    DatetimeArray1D,
    NumberArray1D,
)
from fintime.validation import (
    valid_font_family,
    valid_font_size,
    valid_font_weight,
    valid_color,
    valid_linestyle,
    between_01,
    positive_number,
)


def get_config():

    rcParams["font.sans-serif"] = [
        "Roboto",
        "Helvetica",
        "Arial",
        "Tahoma",
        "Calibri",
        "DejaVu Sans",
        "Lucida Grande",
    ]

    c = Config(create_intermediate_attributes=True)

    c.grid.linestyle = Field("--", validator=valid_linestyle)
    c.grid.linewidth = Field(0.5, validator=positive_number)
    c.grid.color = Field("black", validator=valid_color)
    c.grid.alpha = Field(0.3, float, between_01)
    c.grid.zorder = 0

    # Font settings
    c.font.family = Field("sans-serif", str, valid_font_family)
    c.font.color = Field("black", validator=valid_color)
    c.font.weight = Field(300, object, valid_font_weight)

    # X-axis label settings
    c.xlabel.color = "black"

    # Y-axis label settings
    c.ylabel.font.family = Field(c.font.family, str, valid_font_family)
    c.ylabel.font.color = Field(c.font.color, validator=valid_color)
    c.ylabel.font.weight = Field(c.font.weight, object, valid_font_weight)
    c.ylabel.font.size = Field(18, object, valid_font_size)
    c.ylabel.color = "black"
    c.ylabel.pad = 30

    # Timezone
    c.timezone = tz.gettz("America/New_York")

    # Figure settings
    c.figure.layout = "tight"
    c.figure.facecolor = "#f9f9f9"
    c.figure.title.font.size = 20
    c.figure.title.font.weight = "bold"
    c.figure.title.font.family = c.font.family
    c.figure.title.y = Field(0.98, validator=between_01)
    c.figure.title.color = "black"

    # Panel settings
    c.panel.facecolor = "white"
    c.panel.xaxis.tick.nudge = 0
    c.panel.spine.color = "black"

    # Candlestick settings
    c.candlestick.panel.height = Field(9.0, validator=positive_number)
    c.candlestick.panel.width = Field(None, float)
    c.candlestick.panel.width_per_bar = 0.1
    c.candlestick.padding.ymin = 0.06
    c.candlestick.padding.ymax = 0.06
    c.candlestick.ylabel = "price"

    c.candlestick.zorder = 14
    c.candlestick.body.relwidth = Field(0.8, validator=between_01)
    c.candlestick.body.alpha = Field(1.0, float, validator=between_01)
    c.candlestick.body.face.color.up = Field("#4EA59A", validator=valid_color)
    c.candlestick.body.face.color.down = Field(
        "#E05D57", validator=valid_color
    )
    c.candlestick.body.edge.color.up = "black"
    c.candlestick.body.edge.color.down = "black"
    c.candlestick.body.edge.linewidth = 0.2

    c.candlestick.wick.color = Field("#000000", validator=valid_color)
    c.candlestick.wick.linewidth = 1.0
    c.candlestick.wick.alpha = Field(1.0, float, validator=between_01)
    c.candlestick.doji.color = Field("#000000", validator=valid_color)
    c.candlestick.doji.linewidth = 1.0
    c.candlestick.doji.alpha = Field(1.0, float, validator=between_01)
    c.candlestick.data.types = [
        ("dt", DatetimeArray1D),
        ("open", FloatingArray1D),
        ("high", FloatingArray1D),
        ("low", FloatingArray1D),
        ("close", FloatingArray1D),
    ]

    # Volume settings
    c.volume.zorder = 12
    c.volume.relwidth = Field(1.0, validator=between_01)
    c.volume.alpha = Field(1.0, validator=between_01)
    c.volume.panel.height = Field(3.0, validator=positive_number)
    c.volume.panel.width = Field(None, ftype=float)
    c.volume.panel.width_per_bar = 0.1
    c.volume.panel.ylabel = "volume"
    c.volume.padding.ymax = Field(0.05, validator=positive_number)
    c.volume.data.types = [
        ("dt", DatetimeArray1D),
        ("vol", NumberArray1D),
    ]
    c.volume.face.alpha = Field(1, float, between_01)
    c.volume.face.color.up = Field("#62b2a5", validator=valid_color)
    c.volume.face.color.down = Field("#EC7063", validator=valid_color)
    c.volume.face.color.flat = Field("#a6a6a6", validator=valid_color)
    c.volume.edge.linewidth = Field(0.2, float, positive_number)
    c.volume.edge.color.up = Field("black", validator=valid_color)
    c.volume.edge.color.down = Field("black", validator=valid_color)
    c.volume.edge.color.flat = Field("black", validator=valid_color)

    # Line settings
    c.line.zorder = 8
    c.line.linewidth = 1.0
    c.line.color = Field("#606060", validator=valid_color)
    c.line.linestyle = Field("--", validator=valid_linestyle)
    c.line.panel.width_per_data_point = Field(0.1, float, positive_number)
    c.line.panel.max_width = Field(20, float, positive_number)
    c.line.panel.height = Field(3, float, positive_number)
    c.line.padding.ymin = Field(0.06, float, positive_number)
    c.line.padding.ymax = Field(0.06, float, positive_number)

    # FillBetween settings
    c.fill_between.panel.height = 2
    c.fill_between.panel.width = 3
    c.fill_between.panel.padding.ymin = 0.06
    c.fill_between.panel.padding.ymax = 0.06
    c.fill_between.panel.ylabel = Field(None, str)
    c.fill_between.face.color = "#BCD2E8"
    c.fill_between.edge.color = "#528AAE"
    c.fill_between.edge.linewidth = 0.3
    c.fill_between.alpha = 0.5

    # DivergingBar settings
    c.diverging_bar.panel.height = 3.0
    c.diverging_bar.panel.width = 0.0
    c.diverging_bar.panel.width_per_bar = 0.1
    c.diverging_bar.panel.padding.ymin = 0.0
    c.diverging_bar.panel.padding.ymax = 0.0
    c.diverging_bar.panel.ylabel = Field("hi", str)
    c.diverging_bar.face.color.up = "#BCD2E8"
    c.diverging_bar.face.color.down = "#528AAE"
    c.diverging_bar.edge.color.up = "#528AAE"
    c.diverging_bar.edge.color.down = "black"
    c.diverging_bar.alpha = 1.0
    c.diverging_bar.relwidth = 1.0

    c.disable_intermediate_attribute_creation()
    return c

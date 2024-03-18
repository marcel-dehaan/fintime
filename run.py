from fintime.mock.data import (
    generate_random_trade_ticks,
    add_random_trades,
    add_random_imb,
    add_moving_average,
)
from fintime.mock.data import to_timebar

spans = [1, 10, 30, 300]
ticks = generate_random_trade_ticks(seed=1)
datas = {f"{span}s": to_timebar(ticks, span=span) for span in spans}

for span in spans:
    data = datas[f"{span}s"]
    add_random_imb(data)
    add_random_trades(data, 10)
    add_moving_average(data, 20)

for feat, array in datas["10s"].items():
    print(feat.ljust(6), repr(array[:2]))

# --> dt     array(['2024-03-18T16:43:10.000', '2024-03-18T16:43:20.000'], dtype='datetime64[ms]')
# --> open   array([101.61, 101.61])
# --> high   array([101.76, 101.92])
# --> low    array([101.54, 101.57])
# --> close  array([101.61, 101.57])
# --> vol    array([2824, 2749])
# --> imb    array([ 0.41030182, -0.44632449])
# --> price  array([0., 0.])
# --> side   array([None, None], dtype=object)
# --> size   array([0., 0.])
# --> ma20   array([nan, nan])


from matplotlib.pylab import plt
from fintime.plot import plot, Panel
from fintime.artists import (
    CandleStick,
    Volume,
    DivergingBar,
    FillBetween,
    TradeAnnotation,
    Line,
)


fig = plot(
    specs=[
        Panel(
            artists=[
                CandleStick(),
                FillBetween(y1_feat="low", y2_feat="high"),
                TradeAnnotation(),
                Line(yfeat="ma20"),
            ]
        ),
        Panel(artists=[Volume()]),
        Panel(artists=[DivergingBar(feat="imb")]),
    ],
    data=datas["10s"],
    title="Candlestick & Volume Plotted in Separate Panels",
    save="images/panels_plot.png",
)
plt.show()

# %%


fig = plot(
    specs=[
        Panel(
            artists=[
                CandleStick(config={"candlestick.padding.ymin": 0.2}),
                Volume(
                    twinx=True,
                    config={
                        "volume.edge.linewidth": 1,
                        "volume.face.alpha": 0.3,
                        "volume.edge.alpha": 0.5,
                        "volume.padding.ymax": 2,
                        "volume.relwidth": 1,
                    },
                ),
            ]
        ),
    ],
    data=datas["10s"],
    figsize=(20, 15),
    title="Candlestick & Volume Plotted in the Same Panel",
    save="images/panel_plot.png",
)
plt.show()

# %%


from fintime.plot import Subplot
from fintime.config import get_config

config = get_config()
config.figure.facecolor = "#131722"
config.figure.title.color = "lightgray"
config.panel.facecolor = "#042530"
config.panel.spine.color = config.panel.facecolor
config.grid.color = "lightgray"
config.xlabel.color = "lightgray"
config.ylabel.color = "lightgray"
config.candlestick.body.face.color.up = "#53b987"
config.candlestick.body.face.color.down = "#eb4d5c"
config.candlestick.wick.color = "lightgray"
config.candlestick.doji.color = "lightgray"
config.volume.face.color.up = "#53b987"
config.volume.face.color.down = "#eb4d5c"
config.fill_between.alpha = 0.2
config.trade_annotation.text.bbox.edge.linewidth = 0.5
for side in ["buy", "sell"]:
    config.trade_annotation.arrow.edge.color[side] = "lightgray"
    config.trade_annotation.arrow.face.color[side] = "lightgray"
    config.trade_annotation.text.bbox.edge.color[side] = "lightgray"


subplots = [
    Subplot(
        [
            Panel(
                artists=[
                    CandleStick(data=datas["1s"]),
                    TradeAnnotation(data=datas["1s"]),
                    Line(data=datas["1s"], yfeat="ma20"),
                ]
            ),
            Panel(artists=[Volume(data=datas["1s"])]),
            Panel(artists=[DivergingBar(data=datas["1s"], feat="imb")]),
        ]
    ),
    Subplot(
        [
            Panel(
                artists=[
                    TradeAnnotation(),
                    CandleStick(),
                    Line(yfeat="ma20"),
                    FillBetween(y1_feat="low", y2_feat="high"),
                ]
            ),
            Panel(artists=[Volume()]),
        ],
        data=datas["30s"],
    ),
    Subplot(
        [
            Panel(
                artists=[
                    CandleStick(
                        config={"candlestick.body.face.color.up": "#2c7a99"}
                    ),
                    TradeAnnotation(),
                    Line(yfeat="ma20"),
                ]
            ),
            Panel(artists=[Volume()]),
        ],
        data=datas["300s"],
    ),
]

fig = plot(
    subplots,
    title="OHLCV of Different Temporal Intervals in Their Own Subplots",
    config=config,
    save="images/subplots_plot.png",
)
plt.show()


import matplotlib.pyplot as plt
from fintime.config import get_config

data = datas["30s"]
fig = plt.Figure(figsize=(10, 5))
axes = fig.subplots()
axes.set_xlim(min(data["dt"]), max(data["dt"]))
axes.set_ylim(min(data["low"]), max(data["high"]))
cs_artist = CandleStick(data=data, config=get_config())
cs_artist.draw(axes)
plt.savefig("images/standalone_plot.png")
plt.show()

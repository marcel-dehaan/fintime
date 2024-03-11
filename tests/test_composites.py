import numpy as np
from absl.testing import parameterized
from dataclasses import dataclass

from fintime.artists import Artist
from fintime.composites import Panel, Subplot


@dataclass
class MockArtist(Artist):

    width: float
    height: float
    ymin: float
    ymax: float
    xmin: float | np.timedelta64
    xmax: float | np.timedelta64
    twinx: bool = False

    def __post_init__(self):
        self._twinx = self.twinx

    def get_xmin(self):
        return self.xmin

    def get_xmax(self):
        return self.xmax

    def get_ymin(self):
        return self.ymin

    def get_ymax(self):
        return self.ymax

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def draw(self, axes):
        pass

    def validate(self):
        pass


class TestSubplot(parameterized.TestCase):

    @parameterized.parameters(
        # single panel, dynamic size
        {
            "panels": [
                Panel(
                    artists=[
                        MockArtist(
                            width=20,
                            height=10.5,
                            xmin=3.5,
                            xmax=4.5,
                            ymin=1.5,
                            ymax=2.5,
                        )
                    ]
                )
            ],
            "data": {"k": "v"},
            "size": (None, None),
            "exp": {
                "width": 20,
                "height": 10.5,
                "xmin": 1.5,
                "xmax": 4.5,
                "ymin": 1.5,
                "ymax": 2.5,
                "heights": [10.5],
            },
        },
        # single panel, fixed size
        {
            "panels": [
                Panel(
                    artists=[
                        MockArtist(
                            width=20,
                            height=10,
                            xmin=3.5,
                            xmax=4.5,
                            ymin=1.5,
                            ymax=2.5,
                        )
                    ]
                )
            ],
            "data": {"k": "v"},
            "size": (40.0, 30.0),
            "exp": {
                "width": 40.0,
                "height": 30.0,
                "xmin": 1.5,
                "xmax": 4.5,
                "ymin": 1.5,
                "ymax": 2.5,
                "heights": [10.0],
            },
        },
        # multi panel, dynamic size
        {
            "panels": [
                Panel(
                    artists=[
                        MockArtist(
                            width=20,
                            height=10,
                            xmin=3.5,
                            xmax=4.5,
                            ymin=1.5,
                            ymax=2.5,
                        )
                    ]
                ),
                Panel(
                    artists=[
                        MockArtist(
                            width=25,
                            height=8,
                            xmin=4.0,
                            xmax=5.0,
                            ymin=1.0,
                            ymax=2.0,
                        )
                    ]
                ),
            ],
            "data": {"k": "v"},
            "size": (None, None),
            "exp": {
                "width": 25,
                "height": 18,
                "xmin": 3.5,
                "xmax": 5.0,
                "ymin": 1.0,
                "ymax": 2.5,
                "heights": [10, 8],
            },
        },
    )
    def test_initialization(self, panels, data, size, exp):

        panel = Subplot(panels=panels, data=data, size=size)
        self.assertListEqual(panel._components, panels)
        self.assertEqual(panel._data, data)
        self.assertEqual(panel.get_width(), exp["width"])
        self.assertEqual(panel.get_height(), exp["height"])
        self.assertEqual(panel.get_ymin(), exp["ymin"])
        self.assertEqual(panel.get_ymax(), exp["ymax"])
        self.assertListEqual(panel._get_heights(), exp["heights"])

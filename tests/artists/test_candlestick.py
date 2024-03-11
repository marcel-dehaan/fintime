import numpy as np
from absl.testing import parameterized

from fieldconfig import Config, Field
from fintime.artists import CandleStick
from fintime.types import DatetimeArray1D, FloatingArray1D


def get_mock_candlestick_config():
    cfg = Config(create_intermediate_attributes=True)

    cfg.candlestick.panel.height = 9.0
    cfg.candlestick.panel.width = Field(None, float)
    cfg.candlestick.panel.width_per_bar = 0.1
    cfg.candlestick.padding.ymin = 0.06
    cfg.candlestick.padding.ymax = 0.06
    cfg.candlestick.ylabel = "price"

    cfg.candlestick.zorder = 14
    cfg.candlestick.body.relwidth = 0.8
    cfg.candlestick.body.alpha = 1.0
    cfg.candlestick.body.up_color = "#4EA59A"
    cfg.candlestick.body.down_color = "#E05D57"
    cfg.candlestick.wick.color = "#000000"
    cfg.candlestick.wick.linewidth = 1.0
    cfg.candlestick.wick.alpha = 1.0
    cfg.candlestick.doji.color = "#000000"
    cfg.candlestick.doji.linewidth = 1.0
    cfg.candlestick.doji.alpha = 1.0
    cfg.candlestick.data.types = [
        ("dt", DatetimeArray1D),
        ("open", FloatingArray1D),
        ("high", FloatingArray1D),
        ("low", FloatingArray1D),
        ("close", FloatingArray1D),
    ]
    return cfg


class TestCandleStick(parameterized.TestCase):
    def setUp(self):
        # Set up test data
        self.mock_data_0 = {
            "dt": np.array(["2024-01-01", "2024-01-02"], dtype="datetime64"),
            "open": np.array([100, 110], dtype=float),
            "high": np.array([120, 130], dtype=float),
            "low": np.array([90, 105], dtype=float),
            "close": np.array([115, 125], dtype=float),
        }
        self.mock_data_1 = {
            "dt": np.array(["2024-01-01", "2024-01-02"], dtype="datetime64[D]"),
            "open": np.array([110.0, 120.0], dtype=float),
            "high": np.array([130.0, 140.0], dtype=float),
            "low": np.array([100.0, 115.0], dtype=float),
            "close": np.array([125.0, 135.0], dtype=float),
        }
        self.mock_config = get_mock_candlestick_config()

    def test_init(self):
        # Test initialization without data and config
        candlestick = CandleStick()
        self.assertEqual(candlestick._data, {})
        self.assertEqual(candlestick._cfg, {})
        self.assertEqual(candlestick._twinx, False)

        # Test initialization with data and config
        candlestick = CandleStick(
            data=self.mock_data_0, config=self.mock_config, twinx=True
        )
        self.assertEqual(candlestick._data, self.mock_data_0)
        self.assertEqual(candlestick._cfg, self.mock_config)
        self.assertEqual(candlestick._twinx, True)

    def assertDataEqual(self, d0, d1):
        self.assertEqual(d0.keys(), d1.keys())
        for k, v in d0.items():
            np.testing.assert_array_equal(v, d1[k])

    def test_update_data(self):
        # Test updating data on an initially empty CandleStick instance.
        candlestick = CandleStick()
        candlestick._update_data(data=self.mock_data_0)
        self.assertIsInstance(candlestick._data, dict)
        self.assertDataEqual(candlestick._data, self.mock_data_0)

        # Test updating data on a CandleStick instance with existing data.
        candlestick = CandleStick(data=self.mock_data_0)
        candlestick._update_data(data=self.mock_data_1)
        self.assertDataEqual(candlestick._data, self.mock_data_0)

    def test_get_width(self):
        data = self.mock_data_0
        candlestick = CandleStick(data=data, config=self.mock_config)
        width = candlestick.get_width()
        # config.candlestick.panel.width_per_bar * data['dt].size
        self.assertEqual(width, 0.2)

    def test_get_ylabel(self):
        candlestick = CandleStick(config=self.mock_config, ylabel="Test YLabel")
        ylabel = candlestick.get_ylabel()
        self.assertEqual(ylabel, "Test YLabel")

    def test_get_height(self):
        candlestick = CandleStick(config=self.mock_config)
        height = candlestick.get_height()
        self.assertEqual(height, 9.0)

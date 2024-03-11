import numpy as np
from absl.testing import parameterized
from fintime.utils import is_dt64_array
from datetime import datetime


class TestIsDatetimeArray(parameterized.TestCase):
    """
    Test cases for the is_datetime_array function.
    """

    @parameterized.parameters(
        {
            "name": "Datetime Array (Date)",
            "arr": np.array(["2022-01-01", "2022-01-02"], dtype="datetime64"),
            "exp": True,
        },
        {
            "name": "Datetime Array (Seconds)",
            "arr": np.array(
                ["2022-01-01T12:00:00", "2022-01-02T15:30:45"], dtype="datetime64[s]"
            ),
            "exp": True,
        },
        {
            "name": "Datetime Array (Milliseconds)",
            "arr": np.array(
                ["2022-01-01T12:00:00.500", "2022-01-02T15:30:45.250"],
                dtype="datetime64[ms]",
            ),
            "exp": True,
        },
        {
            "name": "Datetime Array (Nanoseconds)",
            "arr": np.array(
                ["2022-01-01T12:00:00.123456789", "2022-01-02T15:30:45.987654321"],
                dtype="datetime64[ms]",
            ),
            "exp": True,
        },
        {
            "name": "Python Datetime Array",
            "arr": np.array(
                np.array(
                    [datetime(2022, 1, 1, 12, 0, 0), datetime(2022, 1, 2, 15, 30, 45)]
                ),
            ),
            "exp": False,
        },
        {
            "name": "Non-Datetime Array",
            "arr": np.array([1, 2, 3, 4]),
            "exp": False,
        },
    )
    def test(self, name, arr, exp):
        act = is_dt64_array(arr)
        self.assertEqual(act, exp, f"Failed test case: {name}")

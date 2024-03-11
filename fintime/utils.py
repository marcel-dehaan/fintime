import numpy as np
from matplotlib.dates import date2num
from fintime.validation import is_dt64_array


def safe_cast_dt64(arr):
    if is_dt64_array(arr):
        return date2num(arr)
    return arr


def infer_yfeat(data, xfeat) -> str:
    """
    Validate if the specified feat is present in the given data.

    Parameters:
    - data: The data dictionary.
    - feat: The feat to be validated.
    - class_name: (Optional) The name of the class using the validation function.

    Raises:
    - KeyError: If feat is not present in the data.
    """
    if len(data) == 1:
        raise ValueError("no data points passed")
    if len(data) > 2:
        raise KeyError(f"cannot infer yfeat from data {data.keys()}")
    return next(key for key in data if key != xfeat)

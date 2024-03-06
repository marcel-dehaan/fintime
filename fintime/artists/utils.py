import numpy as np
from fintime.types import FloatArray1D


def get_vertical_line_segments(
    b_x: FloatArray1D, b_ymin: FloatArray1D, b_ymax: FloatArray1D
):
    return np.stack(
        (
            np.stack((b_x, b_ymin), axis=1),
            np.stack((b_x, b_ymax), axis=1),
        ),
        axis=1,
    )


def get_horizontal_line_segments(
    b_xmin: FloatArray1D, b_xmax: FloatArray1D, b_y: FloatArray1D
):
    return np.stack(
        (
            np.stack((b_xmin, b_y), axis=1),
            np.stack((b_xmax, b_y), axis=1),
        ),
        axis=1,
    )


def get_rectangle_vertices(
    b_xmin: FloatArray1D,
    b_xmax: FloatArray1D,
    b_ymin: FloatArray1D,
    b_ymax: FloatArray1D,
):
    return np.stack(
        (
            np.stack((b_xmin, b_ymin), axis=1),
            np.stack((b_xmin, b_ymax), axis=1),
            np.stack((b_xmax, b_ymax), axis=1),
            np.stack((b_xmax, b_ymin), axis=1),
        ),
        axis=1,
    )


def to_num_td(dt) -> np.timedelta64:
    "infer bar duration in days"
    td = dt - np.roll(dt, 1)
    td[0] = np.median(td)
    return td / np.timedelta64(1, "D")

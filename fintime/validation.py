from typing import Mapping, Type, Optional
import numpy as np
import matplotlib.colors as mcolors


def positive_number(x):
    return x > 0


def between_01(x):
    return x >= 0 and x <= 1


def valid_color(x):
    try:
        mcolors.to_rgba(x)
        return True
    except ValueError:
        return False


def valid_linestyle(x):
    return x in {"solid", "dashed", "dashdot", "dotted", "-", "--", "-.", ":"}


def valid_font_family(x):
    return x in {"serif", "sans-serif", "cursive", "fantasy", "monospace"}


def valid_font_weight(x):
    if isinstance(x, str):
        return x in {"lighter", "normal", "bold", "bolder"}
    if isinstance(x, int):
        return x >= 100 and x <= 900
    return False


def valid_font_size(x):
    if isinstance(x, (int, float)):
        return x > 0 and x < 100
    if isinstance(x, str):
        return x in {
            "xx-small",
            "x-small",
            "small",
            "medium",
            "large",
            "x-large",
            "xx-large",
        }
    return False


def valid_capstype(x):
    return x in {"butt", "projecting", "round"} or None


def is_dt64_array(arr):
    return np.issubdtype(arr.dtype, np.datetime64)


def check_key_presence(feat, data, class_name=None):
    """
    Validate if the specified feat is present in the given data.

    Parameters:
    - feat: The feat to be validated.
    - data: The data dictionary.
    - class_name: (Optional) The name of the class using the validation function.

    Raises:
    - KeyError: If feat is not present in the data.
    """
    if feat not in data:
        class_info = f" ({class_name})" if class_name else ""
        raise KeyError(
            f"The feat '{feat}' is not present in the data keys{class_info}: {data.keys()}"
        )


def ensure_data_type(feat, data, expected_dtype, class_name=None):
    """
    Validate if the specified feature in the given data has the expected data type.

    Parameters:
    - feat: The feature to be validated.
    - data: The data dictionary.
    - expected_dtype: The expected data type of the feature.
    - class_name: (Optional) The name of the class using the validation function.

    Raises:
    - TypeError: If the feature has an unexpected data type.
    """

    if not isinstance(data[feat], expected_dtype):
        class_info = f" ({class_name})" if class_name else ""
        raise TypeError(
            f"The data type of feature '{feat}' is not as expected{class_info}."
        )


def ensure_same_shape(data, class_name=None):
    """
    Validate if all arrays in the given data dictionary have the same shape.

    Parameters:
    - data: A dictionary where keys represent features, and values are arrays to be validated.
    - class_name: (Optional) The name of the class using the validation function.

    Raises:
    - ValueError: If the arrays for different keys have different shapes.
    """
    shapes = {key: arr.shape for key, arr in data.items()}

    if len(set(shapes.values())) > 1:
        class_info = f" ({class_name})" if class_name else ""
        shape_info = {key: shape for key, shape in shapes.items()}
        raise ValueError(
            f"All arrays must have the same shape for each key{class_info}, but shapes are: {shape_info}."
        )


def validate(
    data,
    data_type_mapping: Mapping[str, Type],
    class_name: Optional[str] = None,
    type_safe: bool = True,
    same_shape: bool = True,
):

    for key, _ in data_type_mapping:
        check_key_presence(key, data, class_name)

    if type_safe:
        for key, expected_dtype in data_type_mapping:
            ensure_data_type(key, data, expected_dtype, class_name)

    if same_shape:
        ensure_same_shape(
            {key: data[key] for key, _ in data_type_mapping},
            class_name=class_name,
        )

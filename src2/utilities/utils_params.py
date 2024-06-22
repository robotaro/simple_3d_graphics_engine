from typing import Any, Union
from src.core import constants
from src.utilities import utils_string


def str2color(color_name: str) -> Any:

    if not isinstance(color_name, str):
        return color_name

    return constants.MATERIAL_COLORS[color_name]


def list2tuple(input_list: tuple):

    if isinstance(input_list, list):
        return tuple(input_list)
    elif isinstance(input_list, tuple):
        return input_list
    else:
        raise TypeError("Input must be a list or tuple")


def dict2bool(input_dict: Any, key: Any, default_value: bool) -> bool:

    if not isinstance(input_dict, dict):
        return default_value

    if key not in input_dict:
        return default_value

    return utils_string.string2bool(input_value=input_dict[key], default_value=default_value)


def dict2int(input_dict: Any, key: Any, default_value: int) -> int:

    if not isinstance(input_dict, dict):
        return default_value

    if key not in input_dict:
        return default_value

    return utils_string.string2int(input_value=input_dict[key], default_value=default_value)


def dict2float(input_dict: Any, key: Any, default_value: float) -> float:

    if not isinstance(input_dict, dict):
        return default_value

    if key not in input_dict:
        return default_value

    return utils_string.string2float(input_value=input_dict[key], default_value=default_value)


def dict2tuple_float(input_dict: Any, key: Any, default_value: tuple) -> tuple:

    if not isinstance(input_dict, dict):
        return default_value

    if key not in input_dict:
        return default_value

    return utils_string.string2tuple_float(input_value=input_dict[key], default_value=default_value)


def dict2tuple_int(input_dict: Any, key: Any, default_value: tuple) -> tuple:

    if not isinstance(input_dict, dict):
        return default_value

    if key not in input_dict:
        return default_value

    return utils_string.string2tuple_int(input_value=input_dict[key], default_value=default_value)


def dict2string(input_dict: Any, key: Any, default_value: str) -> str:

    if not isinstance(input_dict, dict):
        return default_value

    if key not in input_dict:
        return default_value

    if not isinstance(input_dict[key], str):
        return default_value

    return input_dict[key]


def dict2map(input_dict: Any, key: Any, map_dict: dict, default_value: Any) -> Any:

    """
    Finds a value inside dictionary and uses that value as the key for another dictionary
    """

    if not isinstance(input_dict, dict):
        return default_value

    if key not in input_dict:
        return default_value

    if not isinstance(map_dict, dict):
        raise TypeError("[ERROR] Input 'map' must be a dictionary")

    return map_dict.get(input_dict[key], default_value)


def dict2color(input_dict: Any, key: str, default_value: Union[str, tuple]) -> Any:

    """
    Special case of the map where the respective float values of colors are returned
    """

    # Convert default value to its respective color value to be used in case the key is missing
    if default_value in constants.MATERIAL_COLORS:
        default_value = constants.MATERIAL_COLORS[default_value]

    if not isinstance(input_dict, dict):
        return default_value

    if key not in input_dict:
        return default_value

    if input_dict[key] in constants.MATERIAL_COLORS:
        return constants.MATERIAL_COLORS[input_dict[key]]

    return utils_string.string2tuple_float(input_value=input_dict[key], default_value=default_value)


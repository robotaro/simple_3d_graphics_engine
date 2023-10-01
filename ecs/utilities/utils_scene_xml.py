from ecs import constants
from ecs.utilities import utils_string


def get_color(color_str: str, default_color=(0.75, 0.75, 0.75)) -> tuple:
    color_list = utils_string.string2float_tuple(color_str)
    if color_list is None:
        return default_color
    pass
from typing import Any

from ecs.utilities import utils_string


class Component:

    _type = "base_component"

    __slots__ = [
        "parameters",
        "initialised"
    ]

    def __init__(self, parameters: dict):
        self.parameters = parameters
        self.initialised = False

    def initialise(self, **kwargs):
        pass

    def release(self):
        pass

    # From: String  =================================================================================================

    @staticmethod
    def string2bool(input_value: Any, default_value: bool) -> bool:

        if isinstance(input_value, bool):
            return input_value

        if not isinstance(input_value, str):
            return default_value

        try:
            clean_string = input_value.strip(" ").lower()
            if clean_string in ("true", "t", "yes", "y", "1"):
                return True
            if clean_string in ("false", "f", "no", "n", "0"):
                return False
        except Exception:
            return default_value


    @staticmethod
    def string2float(input_value: Any, default_value: float) -> float:
        if isinstance(input_value, float):
            return input_value

        if not isinstance(input_value, str):
            return default_value

        try:
            return float(input_value)
        except Exception:
            return default_value

    @staticmethod
    def string2int(input_value: Any, default_value: int) -> int:
        if isinstance(input_value, int):
            return input_value

        if not isinstance(input_value, str):
            return default_value

        try:
            return int(input_value)
        except Exception:
            return default_value

    @staticmethod
    def string2tuple_float(input_value: Any, default_value: tuple) -> tuple:

        if isinstance(input_value, tuple):
            return input_value

        if not isinstance(input_value, str):
            return default_value

        clean_string = input_value.replace("\t", " ").replace(",", " ").strip(" ")
        try:
            return tuple([float(value) for value in clean_string.split(" ") if len(value) > 0])
        except Exception:
            return default_value

    @staticmethod
    def string2tuple_int(input_value: Any, default_value: tuple) -> tuple:

        if isinstance(input_value, tuple):
            return input_value

        if not isinstance(input_value, str):
            return default_value

        clean_string = input_value.replace("\t", " ").replace(",", " ").strip(" ")
        try:
            return tuple([int(float(value)) for value in clean_string.split(" ") if len(value) > 0])
        except Exception:
            return default_value

    # From: Dictionary =================================================================================================

    @staticmethod
    def dict2bool(input_dict: Any, key: Any, default_value: bool) -> bool:

        if not isinstance(input_dict, dict):
            return default_value

        if key not in input_dict:
            return default_value

        return Component.string2bool(input_value=input_dict[key], default_value=default_value)

    @staticmethod
    def dict2int(input_dict: Any, key: Any, default_value: int) -> int:

        if not isinstance(input_dict, int):
            return default_value

        if key not in input_dict:
            return default_value

        return Component.string2int(input_value=input_dict[key], default_value=default_value)

    @staticmethod
    def dict2float(input_dict: Any, key: Any, default_value: float) -> float:

        if not isinstance(input_dict, float):
            return default_value

        if key not in input_dict:
            return default_value

        return Component.string2float(input_value=input_dict[key], default_value=default_value)

    @staticmethod
    def dict2tuple_float(input_dict: Any, key: Any, default_value: tuple) -> tuple:

        if not isinstance(input_dict, dict):
            return default_value

        if key not in input_dict:
            return default_value

        return Component.string2tuple_float(input_value=input_dict[key], default_value=default_value)

    @staticmethod
    def dict2tuple_int(input_dict: Any, key: Any, default_value: tuple) -> tuple:

        if not isinstance(input_dict, dict):
            return default_value

        if key not in input_dict:
            return default_value

        return Component.string2tuple_int(input_value=input_dict[key], default_value=default_value)
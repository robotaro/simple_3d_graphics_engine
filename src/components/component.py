from typing import Any, Union

from src import constants


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

        if not isinstance(input_dict, dict):
            return default_value

        if key not in input_dict:
            return default_value

        return Component.string2int(input_value=input_dict[key], default_value=default_value)

    @staticmethod
    def dict2float(input_dict: Any, key: Any, default_value: float) -> float:

        if not isinstance(input_dict, dict):
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

    @staticmethod
    def dict2string(input_dict: Any, key: Any, default_value: str) -> str:

        if not isinstance(input_dict, dict):
            return default_value

        if key not in input_dict:
            return default_value

        if not isinstance(input_dict[key], str):
            return default_value

        return input_dict[key]

    @staticmethod
    def dict2map(input_dict: Any, key: Any, map_dict: dict, default_value: Any) -> Any:

        """
        Finds a value inside dictionary and uses that value as the key for another dictionay
        """

        if not isinstance(input_dict, dict):
            return default_value

        if key not in input_dict:
            return default_value

        if not isinstance(map_dict, dict):
            raise TypeError("[ERROR] Input 'map' must be a dictionary")

        return map_dict.get(input_dict[key], default_value)

    @staticmethod
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

        return Component.string2tuple_float(input_value=input_dict[key], default_value=default_value)


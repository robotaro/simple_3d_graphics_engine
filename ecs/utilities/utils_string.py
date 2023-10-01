from typing import List, Union, Tuple


def str2bool(input_string: str) -> bool:
    clean_string = input_string.strip(" ").lower()
    if clean_string in ("true", "t", "yes", "y", "1"):
        return True
    if clean_string  in ("false", "f", "no", "n", "0"):
        return False
    raise ValueError(f"[ERROR] Input string '{input_string}' must be some variation of true or false")


def string2float_tuple(input_string: str) -> Union[Tuple[float], None]:
    clean_string = input_string.replace("\t", " ").replace(",", " ").strip(" ")
    try:
        return tuple([float(value) for value in clean_string.split(" ") if len(value) > 0])
    except Exception:
        return None


def string2int_tuple(input_string: str) -> Union[Tuple[int], None]:
    clean_string = input_string.replace("\t", " ").replace(",", " ").strip(" ")
    try:
        return tuple([int(float(value)) for value in clean_string.split(" ") if len(value) > 0])
    except Exception:
        return None
from typing import List


def str2bool(input_string: str) -> bool:
    clean_string = input_string.strip(" ").lower()
    if clean_string in ("true", "t", "yes", "y", "1"):
        return True
    if clean_string  in ("false", "f", "no", "n", "0"):
        return False
    raise ValueError(f"[ERROR] Input string '{input_string}' must be some variation of true or false")


def string2float_list(input_string: str) -> List[float]:
    clean_string = input_string.replace("\t", " ").replace(",", " ").strip(" ")
    return [float(value) for value in clean_string.split(" ") if len(value) > 0]


def string2int_list(input_string: str) -> List[float]:
    clean_string = input_string.replace("\t", " ").replace(",", " ").strip(" ")
    return [int(float(value)) for value in clean_string.split(" ") if len(value) > 0]

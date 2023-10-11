from typing import  Union, Tuple, Any


def str2bool(input_string: str) -> bool:
    clean_string = input_string.strip(" ").lower()
    if clean_string in ("true", "t", "yes", "y", "1"):
        return True
    if clean_string  in ("false", "f", "no", "n", "0"):
        return False
    raise ValueError(f"[ERROR] Input string '{input_string}' must be some variation of true or false")

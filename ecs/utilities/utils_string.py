from typing import List


def string2float_list(input_string: str) -> List[float]:
    clean_string = input_string.replace("\t", " ").replace(",", " ").strip(" ")
    return [float(value) for value in clean_string.split(" ") if len(value) > 0]


def string2int_list(input_string: str) -> List[float]:
    clean_string = input_string.replace("\t", " ").replace(",", " ").strip(" ")
    return [int(float(value)) for value in clean_string.split(" ") if len(value) > 0]

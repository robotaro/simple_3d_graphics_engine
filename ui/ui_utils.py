
def string2value(input_value: str):
    """
    This function receives a value as a string and converts it to
    a float value depeding on its format:
    - Format A) "10" -> pixels = 10
    - Format B) "10%" -> ratio = 0.1
    :param input_value: string
    :return: float/None, float/None
    """
    if not isinstance(input_value, str):
        raise ValueError("[ERROR] Expected a value as a string")

    value_pixels = None
    value_ratio = None

    if '%' in input_value:
        value_ratio = float(input_value.rstrip('%')) / 100.0
    else:
        value_pixels = float(input_value)
    return value_pixels, value_ratio
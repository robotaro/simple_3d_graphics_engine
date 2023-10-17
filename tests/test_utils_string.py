from src.utilities import utils_string


def test_string2tuple_float():

    test = [
        "12.0 2 45",
        "2.1, 23,9.1",
        "2.3, 45    6.78",
        "test"
    ]
    target = [
        (12.0, 2.0, 45.0),
        (2.1, 23.0, 9.1),
        (2.3, 45.0, 6.78),
        (0.0, 0.0, 0.0)
    ]

    for test, target in zip(test, target):
        result = utils_string.string2tuple_float(input_value=test, default_value=(0.0, 0.0, 0.0))
        assert target == result


def test_string2tuple_int():

    test = [
        "12 2 45",
        "2.1, 23,9.1",
        "2.3, 45    6.78",
        "test"
    ]
    target = [
        (12, 2, 45),
        (2, 23, 9),
        (2, 45, 6),
        (0, 0, 0)
    ]

    for test, target in zip(test, target):
        result = utils_string.string2tuple_int(input_value=test, default_value=(0.0, 0.0, 0.0))
        assert target == result

from ecs.utilities import utils_string


def test_string2float_list():

    test = [
        "12.0 2 45",
        "2.1, 23,9.1",
        "2.3, 45    6.78",
    ]
    target = [
        [12.0, 2.0, 45.0],
        [2.1, 23.0, 9.1],
        [2.3, 45.0, 6.78],
    ]

    for test, target in zip(test, target):
        result = utils_string.string2float_list(input_string=test)
        assert target == result


def test_string2int_list():

    test = [
        "12 2 45",
        "2.1, 23,9.1",
        "2.3, 45    6.78",
    ]
    target = [
        [12, 2, 45],
        [2, 23, 9],
        [2, 45, 6],
    ]

    for test, target in zip(test, target):
        result = utils_string.string2int_list(input_string=test)
        assert target == result

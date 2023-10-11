from src.components.component import Component


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
        result = Component.string2tuple_float(input_value=test, default_value=(0.0, 0.0, 0.0))
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
        (0.0, 0.0, 0.0)
    ]

    for test, target in zip(test, target):
        result = Component.string2tuple_int(input_value=test, default_value=(0.0, 0.0, 0.0))
        assert target == result

def test_dict2int():

    test_dict = {"value_1": 56,
                 "value_2": "76",
                 "value_3": "apple"}
    default_a = 12

    test_condition = [
        ("value_1", 56),
        ("value_2", 76),
        ("value_x", default_a),
        ("value_3", default_a)]

    for key, target in test_condition:
        result = Component.dict2int(input_dict=test_dict, key=key, default_value=default_a)
        assert target == result


def test_dict2float():

    test_dict = {"value_1": 56.3,
                 "value_2": "76.2",
                 "value_3": "orange"}
    default_a = 12.3

    test_condition = [
        ("value_1", 56.3),
        ("value_2", 76.2),
        ("value_x", default_a),
        ("value_3", default_a),
    ]

    for key, target in test_condition:
        result = Component.dict2float(input_dict=test_dict, key=key, default_value=default_a)
        assert target == result


def test_dict2tuple_int():

    test_dict = {"value_1": (56, 11, 0),
                 "value_2": "76 11,0",
                 "value_3": "orange"}
    default_a = (1, 2, 3)

    test_condition = [
        ("value_1", (56, 11, 0)),
        ("value_2", (76, 11, 0)),
        ("value_x", default_a),
        ("value_3", default_a),
    ]

    for key, target in test_condition:
        result = Component.dict2tuple_int(input_dict=test_dict, key=key, default_value=default_a)
        assert target == result


def test_dict2tuple_float():

    test_dict = {"value_1": (56.3, 11.5, 0.3),
                 "value_2": "76.2 11.5,0.3",
                 "value_3": "orange"}
    default_a = (1.0, 2.0, 3.0)

    test_condition = [
        ("value_1", (56.3, 11.5, 0.3)),
        ("value_2", (76.2, 11.5, 0.3)),
        ("value_x", default_a),
        ("value_3", default_a),
    ]

    for key, target in test_condition:
        result = Component.dict2tuple_float(input_dict=test_dict, key=key, default_value=default_a)
        assert target == result



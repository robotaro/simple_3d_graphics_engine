import numpy as np
from src.math import intersection_3d

"""
def test_closest_point():
    #                   a_origin         a_direction      b_origin         b_direction     target
    test_conditions = [((1.0, 2.0, 3.0), (1.0, 0.0, 0.0), (4.0, 5.0, 6.0), (0.0, 1.0, 0.0), 3.0),
                       ((1.0, 1.0, 1.0), (1.0, 0.0, 0.0), (1.0, 1.0, 1.0), (0.0, 1.0, 0.0), 0.0),
                       ((1.0, 1.0, 1.0), (1.0, 0.0, 0.0), (1.0, 2.0, 1.0), (0.0, 1.0, 0.0), -1.0)]

    # Calculate the closest point
    for a_origin, a_direction, b_origin, b_direction, target in test_conditions:
        a_origin = np.array(a_origin, dtype=np.float32)
        a_direction = np.array(a_direction, dtype=np.float32)
        b_origin = np.array(b_origin, dtype=np.float32)
        b_direction = np.array(b_direction, dtype=np.float32)
        result = intersection_3d.closest_point(a_origin,
                                               a_direction,
                                               b_origin,
                                               b_direction)
        assert result == target
    g = 0
"""
import numpy as np
from src.math import intersection_3d


def test_intersect_boolean_ray_sphere():

    #                   ray_origin        ray_direction    sphere_origin   radius  target
    test_conditions = [((0.0, 0.0, -5.0), (0.0, 0.0, 1.0), (0.0, 0.0, 0.0), 0.5, True),
                       ((0.0, -5.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0), 0.5, True),
                       ((-5.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, 0.0), 0.5, True),

                       ((0.0, 0.0, 0.5), (0.0, 0.0, 1.0), (0.0, 0.0, 0.0), 0.5, True),
                       ((0.0, 0.5, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0), 0.5, True),
                       ((0.5, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, 0.0), 0.5, True),

                       ((0.0, 0.0, 0.5), (0.0, 0.0, 1.0), (0.0, 0.0, 0.0), 0.49, True),  # Intersects before origin
                       ((0.0, 0.5, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0), 0.49, True),  # Intersects before origin
                       ((0.5, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, 0.0), 0.49, True),  # Intersects before origin

                       ((0.0, 0.0, -5.0), (0.0, 0.0, 1.0), (0.0, 3.0, 1.0), 0.5, False),
                       ((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, 0.0, 1.0),  0.1, True),
                       ((5.0, 5.0, 5.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0),  0.1, False)]  # Edge case: direction is zero

    for conditions in test_conditions:
        ray_origin = np.array(conditions[0], dtype=np.float32)
        ray_direction = np.array(conditions[1], dtype=np.float32)
        sphere_origin = np.array(conditions[2], dtype=np.float32)
        sphere_radius = float(conditions[3])
        target = conditions[4]

        result = intersection_3d.intersect_boolean_ray_sphere(
            ray_origin=ray_origin,
            ray_direction=ray_direction,
            sphere_origin=sphere_origin,
            sphere_radius=sphere_radius)

        assert result == target


def test_intersect_ray_capsule():

    #                   ray_origin        ray_direction    point_a          point_b          radius     target
    test_conditions = [((0.0, 0.0, -5.0), (0.0, 0.0, 1.0), (0.0, 0.0, 0.0), (0.0, 4.0, 0.0), 0.5,       4.5),
                       ((0.0, -.5, -5.0), (0.0, 0.0, 1.0), (0.0, 0.0, 0.0), (0.0, 4.0, 0.0), 0.5,       -1),  # Just missed it
                       ((0.0, 4, -2.0),   (0.0, 0.0, 1.0), (0.0, 0.0, 0.0), (0.0, 4.0, 0.0), 0.5,       1.5),
                       ((0.0, 5.0, 0.0),  (0.0, -1.0, 0.0), (0.0, 0.0,-1.0),(0.0, 0.0, 1.0), 0.5,       4.5),
                       ((0.0, 5.0, 0.0),  (0.0, -1.0, 0.0),(-1.0, 0.0, 0.0), (1.0, 0.0, 0.0),0.5,       4.5),
                       ((5.0, 0.0, 0.0),  (-1.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 2.0, 0.0),0.5,       3.5),

                       # Edge case where ray passes directly through points A and B
                       ((5.0, 0.0, 0.0),  (-1.0, 0.0, 0.0), (1.0, 0.0, 0.0), (-1.0, 0.0, 0.0),0.5,       -1.0)]

    for conditions in test_conditions:
        ray_origin = np.array(conditions[0], dtype=np.float32)
        ray_direction = np.array(conditions[1], dtype=np.float32)
        point_a = np.array(conditions[2], dtype=np.float32)
        point_b = np.array(conditions[3], dtype=np.float32)
        radius = float(conditions[4])
        target = float(conditions[5])

        result = intersection_3d.intersect_ray_capsule(
            ray_origin=ray_origin,
            ray_direction=ray_direction,
            point_a=point_a,
            point_b=point_b,
            radius=radius)

        assert result == target

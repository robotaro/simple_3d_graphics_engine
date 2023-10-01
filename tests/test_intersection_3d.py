import numpy as np
from ecs.math import intersection_3d


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
        sphere_radius = conditions[3]
        target = conditions[4]

        result = intersection_3d.intersect_boolean_ray_sphere(
            ray_origin=ray_origin,
            ray_direction=ray_direction,
            sphere_origin=sphere_origin,
            sphere_radius=sphere_radius)

        assert target == result


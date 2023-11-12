import numpy as np
from src.math import ray_intersection


def test_plane_from_point_and_normal():

    # XZ plane with Normal Up
    point = np.array([0, 0, 0], dtype=np.float32)
    normal = np.array([1, 0, 0], dtype=np.float32)
    result_plane = ray_intersection.plane_from_point_and_normal(point, normal)
    target = np.array([1, 0, 0, 0], dtype=np.float32)
    np.testing.assert_array_equal(result_plane, target)

    # XZ plane with Normal Down
    point = np.array([0, 0, 0], dtype=np.float32)
    normal = np.array([-1, 0, 0], dtype=np.float32)
    result_plane = ray_intersection.plane_from_point_and_normal(point, normal)
    target = np.array([-1, 0, 0, 0], dtype=np.float32)
    np.testing.assert_array_equal(result_plane, target)

    # XY plane
    point = np.array([0, 0, 0], dtype=np.float32)
    normal = np.array([0, 1, 0], dtype=np.float32)
    result_plane = ray_intersection.plane_from_point_and_normal(point, normal)
    target = np.array([0, 1, 0, 0], dtype=np.float32)
    np.testing.assert_array_equal(result_plane, target)

    # XZ plane with offset
    point = np.array([1, 2, 3], dtype=np.float32)
    normal = np.array([0, 0, 1], dtype=np.float32)
    result_plane = ray_intersection.plane_from_point_and_normal(point, normal)
    target = np.array([0, 0, 1, -3], dtype=np.float32)
    np.testing.assert_array_equal(result_plane, target)


def test_intersect_ray_plane():

    # XY plane with ray pointing towards
    plane_point = np.array([0, 0, 0], dtype=np.float32)
    plane_normal = np.array([0, 0, 1], dtype=np.float32)
    plane = ray_intersection.plane_from_point_and_normal(plane_point, plane_normal)
    ray_origin = np.array([2, 3, 4], dtype=np.float32)
    ray_direction = np.array([0, 0, -1], dtype=np.float32)
    target = 4
    result = ray_intersection.intersect_ray_plane(ray_origin, ray_direction, plane)
    assert result == target

    # XY plane with ray pointing away from
    plane_point = np.array([0, 0, 0], dtype=np.float32)
    plane_normal = np.array([0, 0, 1], dtype=np.float32)
    plane = ray_intersection.plane_from_point_and_normal(plane_point, plane_normal)
    ray_origin = np.array([2, 3, 4], dtype=np.float32)
    ray_direction = np.array([0, 0, 1], dtype=np.float32)
    target = -4
    result = ray_intersection.intersect_ray_plane(ray_origin, ray_direction, plane)
    assert result == target


"""def test_define_plane():

    # Case A) XY plane
    origin = np.array([0, 0, 0], dtype=np.float32)
    vector_1 = np.array([1, 0, 0], dtype=np.float32)
    vector_2 = np.array([0, 1, 0], dtype=np.float32)

    result_plane = ray_intersection.define_plane(origin, vector_1, vector_2)

    target = np.array([0, 0, 1, 0], dtype=np.float32)
    np.testing.assert_array_equal(result_plane, target)

    # Case A) Offset XY plane
    origin = np.array([0, 0, 5], dtype=np.float32)
    vector_1 = np.array([1, 0, 0], dtype=np.float32)
    vector_2 = np.array([0, 1, 0], dtype=np.float32)

    result_plane = ray_intersection.define_plane(origin, vector_1, vector_2)

    target = np.array([0, 0, 1, 5], dtype=np.float32)
    np.testing.assert_array_equal(result_plane, target)

    # Case B) XZ plane
    origin = np.array([0, 0, 0], dtype=np.float32)
    vector_1 = np.array([1, 0, 0], dtype=np.float32)
    vector_2 = np.array([0, 0, 1], dtype=np.float32)

    result_plane = ray_intersection.define_plane(origin, vector_1, vector_2)

    target = np.array([0, -1, 0, 0], dtype=np.float32)
    np.testing.assert_array_equal(result_plane, target)

    # Case B) Ofset XZ plane
    origin = np.array([0, 2, 0], dtype=np.float32)
    vector_1 = np.array([1, 0, 0], dtype=np.float32)
    vector_2 = np.array([0, 0, 1], dtype=np.float32)

    result_plane = ray_intersection.define_plane(origin, vector_1, vector_2)

    # in the plane equation (ax + by + cz + d), the distance d (or w value) is ALWAYS POSITIVE!
    # This is because
    target = np.array([0, -1, 0, 2], dtype=np.float32)
    np.testing.assert_array_equal(result_plane, target)"""


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

        result = ray_intersection.intersect_boolean_ray_sphere(
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

        result = ray_intersection.intersect_ray_capsule(
            ray_origin=ray_origin,
            ray_direction=ray_direction,
            point_a=point_a,
            point_b=point_b,
            radius=radius)

        assert result == target

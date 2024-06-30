from glm import vec3, mat4
from src3 import math_3d


def test_sphere_positive_collisions():

    # Test 1
    ray_origin = vec3(1.57978, 1.10139, 3.83771)
    ray_direction = vec3(-0.220537, -0.0451766, -0.974332)

    collision, _, _ = math_3d.intersect_ray_sphere(
        ray_origin=ray_origin,
        ray_direction=ray_direction,
        sphere_radius=0.2,
        sphere_origin=vec3(1.0, 1.0, 1.0)
    )
    assert collision

    # Test 2
    ray_origin = vec3(-2.28183, -1.10232, 1.13848)
    ray_direction = vec3(0.847191, 0.829928, -0.037799)

    collision, _, _ = math_3d.intersect_ray_sphere(
        ray_origin=ray_origin,
        ray_direction=ray_direction,
        sphere_radius=0.2,
        sphere_origin=vec3(1.0, 1.0, 1.0)
    )
    assert collision


def test_sphere_negative_collisions():

    # Test 1
    ray_origin = vec3(0, 0, 0)
    ray_direction = vec3(1.0, 0.0, 0.0)

    collision, _, _ = math_3d.intersect_ray_sphere(
        ray_origin=ray_origin,
        ray_direction=ray_direction,
        sphere_radius=0.2,
        sphere_origin=vec3(1.0, 1.0, 1.0)
    )
    assert not collision

    # Test 2
    ray_origin = vec3(1.0, 1.5, 1.0)
    ray_direction = vec3(0.0, 1.0, 0.0)

    collision, _, _ = math_3d.intersect_ray_sphere(
        ray_origin=ray_origin,
        ray_direction=ray_direction,
        sphere_radius=0.2,
        sphere_origin=vec3(1.0, 1.0, 1.0)
    )
    assert not collision


def test_capsule_positive_collisions():

    # Test 1
    ray_origin = vec3(1.46255, 0.949182, 3.26144)
    ray_direction = vec3(-0.258437, -0.275761, -0.925833)

    collision = math_3d.intersect_ray_capsule_boolean(
            ray_origin=ray_origin,
            ray_direction=ray_direction,
            radius=0.05,
            p0=vec3(0.0, 0.0, 0.0),
            p1=vec3(1.0, 0.0, 0.0))

    assert collision


def test_capsule_negative_collisions():

    # Collision 1
    ray_origin = vec3(1.0933, 0.736833, 3.08445)
    ray_direction = vec3(0.0556324, -0.228092, -0.972049)

    collision = math_3d.intersect_ray_capsule_boolean(
            ray_origin=ray_origin,
            ray_direction=ray_direction,
            radius=0.05,
            p0=vec3(0.0, 0.0, 0.0),
            p1=vec3(1.0, 0.0, 0.0))

    assert not collision

def test_distance2_ray_segment():

    # Test 1
    ray_origin = vec3(1.0, 1.0, 1.0)
    ray_direction = vec3(1.0, 0.0, 0.0)

    p0 = vec3(2.0, 0.5, 0)
    p1 = vec3(2.0, 0.5, 2.0)

    dist2 = math_3d.distance2_ray_segment(
        ray_origin=ray_origin,
        ray_direction=ray_direction,
        p0=p0,
        p1=p1)

    assert dist2 == 0.5 ** 2

    # Test 2
    ray_origin = vec3(1.0, 1.0, 1.0)
    ray_direction = vec3(1.0, 0.0, 0.0)

    p0 = vec3(2.0, 1.0, 0)
    p1 = vec3(2.0, 1.0, 2.0)

    dist2 = math_3d.distance2_ray_segment(
        ray_origin=ray_origin,
        ray_direction=ray_direction,
        p0=p0,
        p1=p1)

    assert dist2 == 0

    # Test 3
    ray_origin = vec3(1.0, 1.0, 1.0)
    ray_direction = vec3(0.0, 1.0, 0.0)

    p0 = vec3(2.0, 1.0, 0)
    p1 = vec3(2.0, 1.0, 2.0)

    dist2 = math_3d.distance2_ray_segment(
        ray_origin=ray_origin,
        ray_direction=ray_direction,
        p0=p0,
        p1=p1)

    assert dist2 == 1.0


def test_ray_intersects_plane():
    # Test 1: Plane in XY plane, ray perpendicular to plane, plane origin shifted
    plane_origin = vec3(1.0, 1.0, 0.0)
    plane_vec1 = vec3(1.0, 0.0, 0.0)
    plane_vec2 = vec3(0.0, 1.0, 0.0)
    ray_origin = vec3(1.0, 1.0, 1.0)
    ray_direction = vec3(0.0, 0.0, -1.0)

    u, v = math_3d.ray_intersect_plane_coordinates(plane_origin, plane_vec1, plane_vec2, ray_origin, ray_direction)
    assert u == 0.0 and v == 0.0

    # Test 2: Plane in XY plane, ray at an angle, plane origin shifted
    plane_origin = vec3(1.0, 1.0, 0.0)
    ray_origin = vec3(2.0, 2.0, 1.0)
    ray_direction = vec3(0.0, 0.0, -1.0)

    u, v = math_3d.ray_intersect_plane_coordinates(plane_origin, plane_vec1, plane_vec2, ray_origin, ray_direction)
    assert u == 1.0 and v == 1.0

    # Test 3: Plane in YZ plane, ray perpendicular to plane, plane origin shifted
    plane_origin = vec3(1.0, 0.0, 0.0)
    plane_vec1 = vec3(0.0, 1.0, 0.0)
    plane_vec2 = vec3(0.0, 0.0, 1.0)
    ray_origin = vec3(1.0, 1.0, 1.0)
    ray_direction = vec3(-1.0, 0.0, 0.0)

    u, v = math_3d.ray_intersect_plane_coordinates(plane_origin, plane_vec1, plane_vec2, ray_origin, ray_direction)
    assert u == 0.0 and v == 0.0

    # Test 4: Plane in YZ plane, ray at an angle, plane origin shifted
    plane_origin = vec3(1.0, 1.0, 0.0)
    ray_origin = vec3(2.0, 2.0, 0.0)
    ray_direction = vec3(-1.0, -1.0, 0.0)

    u, v = math_3d.ray_intersect_plane_coordinates(plane_origin, plane_vec1, plane_vec2, ray_origin, ray_direction)
    assert u == 1.0 and v == -1.0

    # Test 5: Plane in XZ plane, ray perpendicular to plane, plane origin shifted
    plane_origin = vec3(0.0, 1.0, 0.0)
    plane_vec1 = vec3(1.0, 0.0, 0.0)
    plane_vec2 = vec3(0.0, 0.0, 1.0)
    ray_origin = vec3(0.0, 2.0, 0.0)
    ray_direction = vec3(0.0, -1.0, 0.0)

    u, v = math_3d.ray_intersect_plane_coordinates(plane_origin, plane_vec1, plane_vec2, ray_origin, ray_direction)
    assert u == 0.0 and v == 0.0

    # Test 6: Plane in XZ plane, ray at an angle, plane origin shifted
    plane_origin = vec3(1.0, 1.0, 1.0)
    ray_origin = vec3(2.0, 2.0, 2.0)
    ray_direction = vec3(-1.0, -1.0, -1.0)

    u, v = math_3d.ray_intersect_plane_coordinates(plane_origin, plane_vec1, plane_vec2, ray_origin, ray_direction)
    assert u == 0.0 and v == 0.0

    # Test 7: Plane in arbitrary orientation, ray intersects
    plane_origin = vec3(1.0, 1.0, 1.0)
    plane_vec1 = vec3(1.0, 1.0, 0.0)
    plane_vec2 = vec3(1.0, -1.0, 0.0)
    ray_origin = vec3(2.0, 2.0, 2.0)
    ray_direction = vec3(-1.0, -1.0, -1.0)

    u, v = math_3d.ray_intersect_plane_coordinates(plane_origin, plane_vec1, plane_vec2, ray_origin, ray_direction)
    assert u == 1.0 and v == 0.0

    # Test 8: Plane in arbitrary orientation, ray intersects at an angle
    plane_origin = vec3(1.0, 1.0, 1.0)
    plane_vec1 = vec3(1.0, 0.0, 1.0)
    plane_vec2 = vec3(0.0, 1.0, 1.0)
    ray_origin = vec3(2.0, 2.0, 2.0)
    ray_direction = vec3(-1.0, -1.0, -1.0)

    u, v = math_3d.ray_intersect_plane_coordinates(plane_origin, plane_vec1, plane_vec2, ray_origin, ray_direction)
    assert u == 0.5 and v == 0.5
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
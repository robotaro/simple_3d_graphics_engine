import numpy as np
from numba import njit


@njit(cache=True)
def intersect_boolean_ray_sphere(ray_origin: np.array,
                                 ray_direction: np.array,
                                 sphere_origin: np.array,
                                 sphere_radius: float) -> bool:

    """
    Formula from:
    https://viclw17.github.io/2018/07/16/raytracing-ray-sphere-intersection

    The intersection is true even for values that are

    This function only tests if there is an intersection, not where it occurs specifically. This will need to be
    implemented

    :param ray_origin: Numpy array (3,) <float32>
    :param ray_direction: Numpy array (3,) <float32>
    :param sphere_origin: Numpy array (3,) <float32>
    :param sphere_radius: float
    :return: bool
    """

    sphere_to_ray = ray_origin - sphere_origin
    a = np.dot(ray_direction, ray_direction)
    if a == 0.0:  # Ray has direction (0, 0, 0)
        return False
    b = 2 * np.dot(sphere_to_ray, ray_direction)
    c = np.dot(sphere_to_ray, sphere_to_ray) - sphere_radius * sphere_radius
    discriminant = b * b - 4 * a * c
    return discriminant >= 0  # Return if at least one intersection exists

@njit(cache=True)
def intersect_distance_ray_sphere(ray_origin: np.array,
                                  ray_direction: np.array,
                                  sphere_origin: np.array,
                                  sphere_radius: float) -> float:

    """
    Formula from:
    https://viclw17.github.io/2018/07/16/raytracing-ray-sphere-intersection

    The intersection is true even for values that are

    This function only tests if there is an intersection, not where it occurs specifically. This will need to be
    implemented

    :param ray_origin: Numpy array (3,) <float32>
    :param ray_direction: Numpy array (3,) <float32>
    :param sphere_origin: Numpy array (3,) <float32>
    :param sphere_radius: float
    :return: bool
    """

    sphere_to_ray = ray_origin - sphere_origin
    a = np.dot(ray_direction, ray_direction)
    if a == 0.0:
        return -1.0
    b = 2 * np.dot(sphere_to_ray, ray_direction)
    c = np.dot(sphere_to_ray, sphere_to_ray) - sphere_radius * sphere_radius
    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return -1.0
    return (-b - np.sqrt(discriminant)) / (2.0 * a)


@njit
def ray_cylinder_intersection(ray_origin: np.array,
                              ray_direction: np.array,
                              cylinder_start: np.array,
                              cylinder_end: np.array,
                              cylinder_radius: float):
    # Calculate the vector representing the axis of the cylinder
    cylinder_axis = cylinder_end - cylinder_start

    # Calculate the vector from the ray's origin to the cylinder's start point
    ray_to_cylinder_start = cylinder_start - ray_origin

    # Calculate the coefficients for the quadratic equation
    a = np.dot(ray_direction - np.dot(ray_direction, cylinder_axis) * cylinder_axis, ray_direction - np.dot(ray_direction, cylinder_axis) * cylinder_axis)
    b = 2.0 * np.dot(ray_direction - np.dot(ray_direction, cylinder_axis) * cylinder_axis, ray_to_cylinder_start - np.dot(ray_to_cylinder_start, cylinder_axis) * cylinder_axis)
    c = np.dot(ray_to_cylinder_start - np.dot(ray_to_cylinder_start, cylinder_axis) * cylinder_axis, ray_to_cylinder_start - np.dot(ray_to_cylinder_start, cylinder_axis) * cylinder_axis) - cylinder_radius**2

    # Calculate the discriminant
    discriminant = b**2 - 4*a*c

    if discriminant >= 0:
        # At least one intersection point exists
        return True

    return False

@njit
def ray_box_intersection(ray_origin, ray_direction, box_min, box_max):
    t_min = (box_min - ray_origin) / ray_direction
    t_max = (box_max - ray_origin) / ray_direction

    t1 = np.min(t_min)
    t2 = np.max(t_max)

    if t1 <= t2:
        #t_near = t1
        t_far = t2

        if t_far >= 0:
            return True

    return False

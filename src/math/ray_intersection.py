import numpy as np
from numba import njit, float32

# Constants
FLT_EPSILON = np.finfo(float).eps

# ======================================================================================================================
#                                                Ray / Ray
# ======================================================================================================================


@njit(float32[:](float32[:], float32[:], float32[:], float32[:]), cache=True)
def ray2ray_nearest_point(ray_0_origin, ray_0_direction, ray_1_origin, ray_1_direction):

    """
    Original function from Gizmo project: https://github.com/john-chapman/im3d/blob/master/im3d.cpp
    :param ray_0_origin:
    :param ray_0_direction:
    :param ray_1_origin:
    :param ray_1_direction:
    :return:
    """

    p = ray_0_origin - ray_1_origin
    q = np.dot(ray_0_direction, ray_1_direction)
    s = np.dot(ray_1_direction, p)

    d = 1.0 - q * q

    if d < FLT_EPSILON:  # lines are parallel
        t0_ = 0.0
        t1_ = s
    else:
        r = np.dot(ray_0_direction, p)
        t0_ = (q * s - r) / d
        t1_ = (s - q * r) / d

    return np.array([t0_, t1_], dtype=float32)


# ======================================================================================================================
#                                                Ray / Sphere
# ======================================================================================================================


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

# ======================================================================================================================
#                                                Ray / capsule
# ======================================================================================================================


# Check this for performance warning explanation for '::1': https://github.com/numba/numba/issues/8739
@njit(float32(float32[:], float32[:], float32[:], float32[:], float32), cache=True)
def intersect_ray_capsule(ray_origin, ray_direction, point_a, point_b, radius) -> float:
    """
    Original code from: https://iquilezles.org/articles/intersectors/

    :param ray_origin: np.array, (3,) <float32>
    :param ray_direction: np.array, (3,) <float32>
    :param point_a: np.array, (3,) <float32>
    :param point_b: np.array, (3,) <float32>
    :param radius: <float32>
    :return:
    """

    ba = point_b - point_a
    oa = ray_origin - point_a

    baba = np.dot(ba, ba)
    bard = np.dot(ba, ray_direction)
    baoa = np.dot(ba, oa)
    rdoa = np.dot(ray_direction, oa)
    oaoa = np.dot(oa, oa)

    a = baba - bard * bard

    # Edge-case-fix added by Me! If the ray passes through point A and B, a = 0 and it causes a division by zero.
    if a == 0.0:
        return -1

    b = baba * rdoa - baoa * bard
    c = baba * oaoa - baoa * baoa - radius * radius * baba

    h = b * b - a * c

    if h >= 0.0:
        t = (-b - np.sqrt(h)) / a
        y = baoa + t * bard

        # body
        if 0.0 < y < baba:
            return t

        # caps
        oc = oa if y <= 0.0 else ray_origin - point_b
        b = np.dot(ray_direction, oc)
        c = np.dot(oc, oc) - radius * radius
        h = b * b - c

        if h > 0.0:
            return -b - np.sqrt(h)
    return -1.0

# Check this for performance warning explanation for '::1': https://github.com/numba/numba/issues/8739
@njit(cache=True)
def intersect_ray_capsules(ray_origin, ray_direction, points_a, points_b, radius, output_distances):

    for index in range(points_a.shape[0]):
        output_distances[index] = intersect_ray_capsule(ray_origin,
                                                        ray_direction,
                                                        points_a[index, :],
                                                        points_b[index, :],
                                                        radius)


# ======================================================================================================================
#                                                Ray / Cylinder
# ======================================================================================================================

# UNTESTED
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
    discriminant = b ** 2 - 4 * a * c

    if discriminant >= 0:
        # At least one intersection point exists
        return True

    return False

# ======================================================================================================================
#                                                Ray / Plane
# ======================================================================================================================


float32(float32[:], float32[:])
@njit(cache=True)
def plane_from_point_and_normal(point, normal):

    # Normalize the normal vector
    normal = normal / np.linalg.norm(normal)

    # The plane equation is Ax + By + Cz + D = 0, where [A,B,C] is the normal vector
    # and D can be found by inserting a known point on the plane into the equation.
    D = -np.dot(normal, point)

    # The coefficients are [A, B, C, D]
    coefficients = np.append(normal, D)
    return coefficients


float32(float32[:], float32[:], float32[:])
@njit(cache=True)
def intersect_ray_plane(r_origin: np.array, r_vector: np.array, plane: np.array) -> float:
    # in the plane equation (ax + by + cz + d), the distance d (or W value) is ALWAYS POSITIVE!
    # This is because W is the POSITIVE offset from the origin

    # Calculate numerator and denominator for the intersection formula
    numerator = np.dot(plane[:3], r_origin) + plane[3]
    denominator = np.dot(plane[:3], r_vector)

    # Check if the denominator is too small, implying parallelism
    if np.abs(denominator) < FLT_EPSILON:
        # The ray is parallel to the plane, so there is no intersection
        return -1.0

    # Consider any negative values as the ray point AWAY from the plane or being parallel to it
    return -(numerator / denominator)


@njit(cache=True)
def intersect_ray_plane_old(plane_origin: np.array,
                        plane_normal: np.array,
                        ray_origin: np.array,
                        ray_direction_normalised: np.array):

    """
    Original equation from https://en.wikipedia.org/wiki/Line%E2%80%93plane_intersection

    # WARNING! Ray direction must be normalised!

    :param plane_origin: Numpy array (3,) <float32>
    :param plane_normal:  Numpy array (3,) <float32>
    :param ray_origin:  Numpy array (3,) <float32>
    :param ray_direction:  Numpy array (3,) <float32>
    :return: point of intersection in space or an array of NaN if the ray and the plane are parallel
    """

    num = np.dot((plane_origin - ray_origin), plane_normal)
    den = np.dot(ray_direction_normalised, plane_normal)

    if den == 0:
        temp = np.empty_like(plane_origin)
        temp[:] = np.nan
        return temp
    else:
        return ray_origin + (num / den) * ray_direction_normalised

# UNTESTED
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


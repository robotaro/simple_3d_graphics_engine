import numpy as np
from numba import jit, float32

@jit(nopython=True, cache=True)
def intersect_ray_sphere(ray_origin: np.array,
                         ray_direction: np.array,
                         sphere_position: np.array,
                         sphere_radius: float) -> bool:

    """
    Formula from:
    https://viclw17.github.io/2018/07/16/raytracing-ray-sphere-intersection/#:~:text=When%20the%20ray%20and%20sphere,equations%20and%20solving%20for%20t.

    This function only tests if there is an intersection, not where it occurs specifically. This will need to be
    implemented

    :param ray_origin: Numpy array (3,) <float32>
    :param ray_direction: Numpy array (3,) <float32>
    :param sphere_position: Numpy array (3,) <float32>
    :param sphere_radius: float
    :return: bool
    """

    oc = ray_origin - sphere_position
    a = np.dot(ray_direction, ray_direction)
    b = 2 * np.dot(oc, ray_direction)
    c = np.dot(oc, oc) - sphere_radius * sphere_radius
    discriminant = b*b - 4*a*c
    if discriminant < 0:
        return False
    else:
        return True

@jit(nopython=True, cache=True)
def intersect_ray_plane(plane_origin: np.array,
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


@jit(nopython=True, cache=True)
def point_on_segment(seg_a: np.array,
                     seg_b: np.array,
                     point: np.array):

    """
    This measures the distance between a point and its closes perpendicular projection on a line segment.
    Code based on: https://github.com/CedricGuillemet/ImGuizmo/blob/master/ImGuizmo.cpp
    :param seg_a: Numpy array (3,) <float32>
    :param seg_b: Numpy array (3,) <float32>
    :param point: Numpy array (3,) <float32>
    :return: Numpy array (3,) <float32>
    """

    c = point - seg_a
    v = seg_b - seg_a
    v /= np.linalg.norm(v)

    d = np.linalg.norm(seg_b - seg_a)
    t = np.dot(v, c)

    if t < 0:
        return seg_a

    if t > d:
        return seg_b

    return seg_a + v * t

@jit(float32(float32), nopython=True, cache=True)
def clip01(value: np.float32):
    if value > 1:
        return 1.0
    if value < 0:
        return 0.0
    return value

@jit(nopython=True)
def lerp(point_a: np.array, point_b: np.array, t: np.float32):

    delta = point_b - point_a
    return (point_a + delta * t).astype(np.float32)

@jit(nopython=True, cache=True)
def point_on_segment2(seg_a: np.array,
                      seg_b: np.array,
                      point: np.array):
    seg_ba = seg_b - seg_a
    t = np.dot(point - seg_a, seg_ba) / np.dot(seg_ba, seg_ba)
    return lerp(seg_a, seg_b, clip01(t))

@jit(nopython=True, cache=True)
def lines_closest_points(seg_a: np.array,
                         seg_b: np.array,
                         seg_c: np.array,
                         seg_d: np.array):

    """
    Original code from: https://zalo.github.io/blog/closest-point-between-segments/
    :param seg_a:
    :param seg_b:
    :param seg_c:
    :param seg_d:
    :return: point on ab, point on cd, dist_sqr between points
    """

    seg_dc = seg_d - seg_c
    line_dir_sqr_mag = np.dot(seg_dc, seg_dc)
    in_plane_a = seg_a - ((np.dot(seg_a - seg_c, seg_dc) / line_dir_sqr_mag) * seg_dc)
    in_plane_b = seg_b - ((np.dot(seg_b - seg_c, seg_dc) / line_dir_sqr_mag) * seg_dc)
    in_plane_ba = in_plane_b - in_plane_a
    t = np.dot(seg_c - in_plane_a, in_plane_ba) / np.dot(in_plane_ba, in_plane_ba)
    if np.array_equal(in_plane_a, in_plane_b):
        t = 0
    seg_ab_to_line_cd = lerp(seg_a, seg_b, clip01(t))
    seg_cd_to_seg_ab = point_on_segment2(seg_a=seg_c,
                                         seg_b=seg_d,
                                         point=seg_ab_to_line_cd)
    seg_ab_to_seg_cd = point_on_segment2(seg_a=seg_a,
                                         seg_b=seg_b,
                                         point=seg_cd_to_seg_ab)

    dist2 = np.sum((seg_cd_to_seg_ab - seg_ab_to_seg_cd) ** 2)

    return seg_ab_to_seg_cd, seg_cd_to_seg_ab, dist2


@jit(nopython=True, cache=True)
def distance_point_plane(plane_origin: np.array,
                         plane_normal: np.array,
                         point: np.array):

    # WARNING: Broken function!!!!
    return np.dot(plane_normal, point) + np.dot(plane_normal, plane_origin)


import numpy as np
from numba import njit


def _transform_vector(transform, vector):
    """Apply affine transformation (4-by-4 matrix) to a 3D vector."""
    return (transform @ np.concatenate([vector, np.array([1])]))[:3]


def _transform_direction(transform, vector):
    """Apply affine transformation (4-by-4 matrix) to a 3D directon."""
    return (transform @ np.concatenate([vector, np.array([0])]))[:3]

def normalize(x):
    return x / np.linalg.norm(x)


def look_at(position, target, up):
    """
    Create an affine transformation that locates the camera at `position`, s.t. it looks at `target`.
    :param position: The 3D position of the camera in world coordinates.
    :param target: The 3D target where the camera should look at in world coordinates.
    :param up: The vector that is considered to be up in world coordinates.
    :return: Returns the 4-by-4 affine transform that transforms a point in world space into the camera space, i.e.
      it returns the inverse of the camera's 6D pose matrix. Assumes right-multiplication, i.e. x' = [R|t] * x.
    """

    forward = normalize(position - target)  # forward actually points in the other direction than `target` is.
    right = normalize(np.cross(up, forward))
    camera_up = np.cross(forward, right)

    # We directly create the inverse matrix (i.e. world2cam) because this is typically how look-at is define.
    rot = np.eye(4)
    rot[0, :3] = right
    rot[1, :3] = camera_up
    rot[2, :3] = forward

    trans = np.eye(4)
    trans[:3, 3] = -position

    return rot @ trans


def orthographic_projection(scale_x: float, scale_y: float, z_near: float, z_far: float):
    """Returns an orthographic projection matrix."""
    projection = np.zeros((4, 4), dtype=np.float32)
    projection[0, 0] = 1.0 / scale_x
    projection[1, 1] = 1.0 / scale_y
    projection[2, 2] = 2.0 / (z_near - z_far)
    projection[2, 3] = (z_far + z_near) / (z_near - z_far)
    projection[3, 3] = 1.0
    return projection


def perspective_projection(fov_rad: float, aspect_ratio: float, z_near: float, z_far: float):
    """Returns a perspective projection matrix."""
    ar = aspect_ratio
    t = np.tan(fov_rad / 2.0)

    projection = np.zeros((4, 4), dtype=np.float32)
    projection[0, 0] = 1.0 / (ar * t)
    projection[1, 1] = 1.0 / t
    projection[3, 2] = -1.0

    f, n = z_far, z_near
    if f is None:
        projection[2, 2] = -1.0
        projection[2, 3] = -2.0 * n
    else:
        projection[2, 2] = (f + n) / (n - f)
        projection[2, 3] = (2 * f * n) / (n - f)

    return projection

import numpy as np
from numba import njit, float32
from src.math import mat3

DEG2RAD = np.pi / 180.0


def compute_transform(position: tuple, rotation_rad: tuple, scale=1.0, order='xyz'):

    """
    #TODO: This is a SLOW implementation! Hard-code it if you are only going o use one rotation,
    #      and use Numba instead.

    Returns a 3x3 rotation matrix based on the angles and the rotation order
    :param x_rad: Angle in radians
    :param y_rad: Angle in radians
    :param z_rad: Angle in radians
    :param order: string with the order of axes
    :return: numpy ndarray (3, 3) <float32>
    """

    cx = np.cos(rotation_rad[0])
    sx = np.sin(rotation_rad[0])
    cy = np.cos(rotation_rad[1])
    sy = np.sin(rotation_rad[1])
    cz = np.cos(rotation_rad[2])
    sz = np.sin(rotation_rad[2])

    rx = np.asarray([[1, 0, 0],
                     [0, cx, -sx],
                     [0, sx, cx]])
    ry = np.asarray([[cy, 0, sy],
                     [0, 1, 0],
                     [-sy, 0, cy]])
    rz = np.asarray([[cz, -sz, 0],
                     [sz, cz, 0],
                     [0, 0, 1]])

    rotation = np.eye(3, dtype=np.float32)

    for axis in order.lower():
        if axis == 'x':
            rotation = np.matmul(rotation, rx)
        elif axis == 'y':
            rotation = np.matmul(rotation, ry)
        else:
            rotation = np.matmul(rotation, rz)

    rotation *= scale

    transform = np.eye(4, dtype=np.float32)
    transform[:3, :3] = rotation
    transform[:3, 3] = position

    return transform


@njit(float32[:, :](float32[:], float32[:], float32))
def create_transform_xyz(position: np.array, rotation: np.array, scale: float):
    """

    WORK IN PROGRESS

    :param position:
    :param rotation:
    :param scale:
    :return:
    """
    alpha, beta, gamma = rotation

    s_alpha = np.sin(alpha)
    c_alpha = np.cos(alpha)
    s_beta = np.sin(beta)
    c_beta = np.cos(beta)
    s_gamma = np.sin(gamma)
    c_gamma = np.cos(gamma)

    transform = np.eye(4, dtype=np.float32)

    # Rotation and scale
    """transform[0, 0] = cy * cz * scale
    transform[1, 0] = -cy * sz * scale
    transform[2, 0] = sy * scale
    transform[0, 1] = sx * sy * cz + cx * sz * scale
    transform[1, 1] = -sx * sy * sz + cx * cz * scale
    transform[2, 1] = -sx * cy * scale
    transform[0, 2] = -cx * sy * cz + sx * sz * scale
    transform[1, 2] = cx * sy * sz + sx * cz * scale
    transform[2, 2] = cx * cy * scale"""

    transform[0, 0] = c_beta * c_alpha * scale
    transform[1, 0] = s_gamma * s_beta * c_alpha - c_gamma * s_alpha * scale
    transform[2, 0] = c_gamma * s_beta * c_alpha + s_gamma * s_alpha * scale
    transform[0, 1] = c_beta * s_alpha * scale
    transform[1, 1] = s_gamma * s_beta * s_alpha + c_gamma * c_alpha * scale
    transform[2, 1] = c_gamma * s_beta * s_alpha - s_gamma * c_alpha * scale
    transform[0, 2] = -s_beta * scale
    transform[1, 2] = s_gamma * c_beta * scale
    transform[2, 2] = c_gamma * c_beta * scale

    # Position
    transform[0, 3] = position[0]
    transform[1, 3] = position[1]
    transform[2, 3] = position[2]

    return transform


@njit(cache=True)
def mul_vector3(in_mat4: np.ndarray, in_vec3: np.array):
    return np.dot(in_mat4[:3, :3], in_vec3) + in_mat4[:3, 3]


@njit(cache=True)
def fast_inverse(in_mat4: np.ndarray, out_mat4: np.ndarray):
    # IMPORTANT: This matrix assumes out_mat4 was already initialised as eye(4)!!!
    out_mat4[:3, :3] = np.linalg.inv(np.ascontiguousarray(in_mat4[:3, :3]))
    out_mat4[:3, 3] = -out_mat4[:3, :3] @ in_mat4[:3, 3]


@njit(cache=True)
def even_faster_inverse(in_mat4: np.ndarray, out_mat4: np.ndarray):
    # IMPORTANT: This matrix assumes out_mat4 was already initialised as eye(4)!!!
    out_mat4[:3, :3] = in_mat4[:3, :3].T  # R.T == R^-1
    out_mat4[:3, 3] = -out_mat4[:3, :3] @ in_mat4[:3, 3]


@njit(cache=True)
def compute_transform_not_so_useful(pos: tuple, rot: tuple, scale: float):
    # TODO: refactor this to simplify scale!

    rotation = np.eye(4)
    rotation[:3, :3] = np.array(rot)

    trans = np.eye(4)
    trans[:3, 3] = np.array(pos)

    scale = np.diag([scale, scale, scale, 1])

    return (trans @ rotation @ scale).astype("f4")


def create(position: np.array, rotation: mat3):

    mat = np.eye(4, dtype=np.float32)
    mat[:3, :3] = rotation
    mat[:3, 3] = position
    return mat


def normalize(x):
    return x / np.linalg.norm(x)


def look_at(position: np.array, target: np.array, up: np.array):

    direction = position - target

    rotation_mat = np.empty((3, 3), dtype=np.float32)
    mat3.look_at_direction(direction=direction, up_vector=up, output_mat3=rotation_mat)

    trans = np.eye(4)
    trans[:3, :3] = rotation_mat
    trans[:3, 3] = position

    return trans


def look_at_direction(position: np.array, direction: np.array, up: np.array):

    rotation_mat = np.empty((3, 3), dtype=np.float32)
    mat3.look_at_direction(direction=direction, up_vector=up, output_mat3=rotation_mat)

    transform = np.eye(4)
    transform[:3, :3] = rotation_mat
    transform[:3, 3] = position

    return transform


def look_at_inverse(position: np.array, target: np.array, up: np.array):
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


def perspective_projection(fovy_rad: float, aspect: float, near: float, far: float):

    """
    Calculates the 4x4 perspective matrix

    :param fovy_rad: Vertical view angle in radians
    :param aspect: aspect ratio of the screen (width / height)
    :param near: Closest point that can be rendered inside the view frustum
    :param far: Furthest point that can be render inside the view frustum
    :return: numpy ndarray (4, 4) <float32>
    """

    s = 1.0 / np.tan(fovy_rad)
    sx, sy = s / aspect, s
    zz = (far + near) / (near - far)
    zw = 2 * far * near / (near - far)
    return np.array([[sx, 0, 0, 0],
                     [0, sy, 0, 0],
                     [0, 0, zz, zw],
                     [0, 0, -1, 0]], dtype=np.float32)


def orthographic_projection(left: float, right: float, bottom: float, top: float, near: float, far: float):
    dx = right - left
    dy = top - bottom
    dz = far - near
    rx = -(right + left) / (right - left)
    ry = -(top + bottom) / (top - bottom)
    rz = -(far + near) / (far - near)
    return np.array([[2.0 / dx, 0, 0, rx],
                     [0, 2.0 / dy, 0, ry],
                     [0, 0, -2.0 / dz, rz],
                     [0, 0, 0, 1]], dtype=np.float32)

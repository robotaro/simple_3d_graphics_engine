from numba import njit
import numpy as np
from numba import njit
from core.math import mat3
from functools import lru_cache

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

@njit
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


def mul_vector(tr_mat4: np.ndarray, vector3: np.array):

    return np.matmul(tr_mat4[0:3, 0:3], vector3) + tr_mat4[:3, 3]


def perspective_projection(fovy_deg, aspect, near, far):

    """
    Calculates the 4x4 perspective matrix

    :param fovy_rad: Vertical view angle in radians
    :param aspect: aspect ratio of the screen (width / height)
    :param near: Closest point that can be rendered inside the view frustum
    :param far: Furthest spoint that can be render inside the view frustum
    :return: numpy ndarray (4, 4) <float32>
    """

    s = 1.0 / np.tan(fovy_deg * DEG2RAD / 2.0)
    sx, sy = s / aspect, s
    zz = (far + near) / (near - far)
    zw = 2 * far * near / (near - far)
    return np.array([[sx, 0, 0, 0],
                     [0, sy, 0, 0],
                     [0, 0, zz, zw],
                     [0, 0, -1, 0]], dtype=np.float32)


def orthographic(left, right, bottom, top, near, far):
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



# ==========[ 3rd party to be removed ]==========
"""
def _perspective(n, f, t, b, l, r):
    return np.array([
        [ 2*n/(r-l),     0    ,   (r+l)/(r-l) ,       0        ],
        [     0    , 2*n/(t-b),   (t+b)/(t-b) ,       0        ],
        [     0    ,     0    , -((f+n)/(f-n)), -(2*n*f/(f-n)) ],
        [     0    ,     0    ,       -1      ,       0        ],
    ])

def perspective(fovy, aspect, near, far):
    top = near * np.tan(fovy / 2)
    right = top * aspect
    return _perspective(near, far, top, -top, -right, right)
"""
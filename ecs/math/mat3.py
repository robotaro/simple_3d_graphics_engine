from numba import njit
import numpy as np
from ecs.math import quaternion


@njit
def look_at_direction(direction: np.array, up_vector: np.array, output_mat3: np.array):

    """
    Check vector multiplication reference at:
    https://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/lookat-function
    [WARNING] The matrices shown on the website are transposed!

    [IMPORTANT] The resulting rotation matrix will have the Z-vector POINTING AT the "direction vector"

    Create a rotation 3x3 matrix where the Z-axis points at the "direction" vector
    :param direction: numpy array (3,) <np.float32>
    :param up_vector: numpy array (3,) <np.float32>
    :param output_mat3:
    """

    # TODO: Add edge-case where direction == up_vector

    forward = direction / np.linalg.norm(direction)
    right = np.cross(up_vector, forward)
    right /= np.linalg.norm(right)
    up = np.cross(forward, right)

    output_mat3[:, 0] = right
    output_mat3[:, 1] = up
    output_mat3[:, 2] = forward


@njit
def rotate_around_vector(vector, angle, output_mat3):
    """
    Implementation based on description from : http://scipp.ucsc.edu/~haber/ph216/rotation_12.pdf
    Creates a rotation matrix around a defined direction determined by "vector" with angle equals to "angle"

    :param vector: numpy array (3, ) <np.float32>
    :param angle: float angle in radians
    :param output_mat3: Pre-allocated  ndarray (3, 3) <np.float32> used for output result
    """

    vector_norm = vector / np.linalg.norm(vector)

    sin = np.sin(angle)
    cos = np.cos(angle)
    one_cos = 1.0 - cos
    n1 = vector_norm[0]
    n2 = vector_norm[1]
    n3 = vector_norm[2]
    n1n2_one_cos = n1 * n2 * one_cos
    n1n3_one_cos = n1 * n3 * one_cos
    n2n3_one_cos = n2 * n3 * one_cos
    n1sin = n1 * sin
    n2sin = n2 * sin
    n3sin = n3 * sin

    # Column 1
    output_mat3[0, 0] = cos + (n1 * n1 * one_cos)
    output_mat3[1, 0] = n1n2_one_cos + n3sin
    output_mat3[2, 0] = n1n3_one_cos - n2sin

    # Column 2
    output_mat3[0, 1] = n1n2_one_cos - n3sin
    output_mat3[1, 1] = cos + (n2 * n2 * one_cos)
    output_mat3[2, 1] = n2n3_one_cos + n1sin

    # Column 3
    output_mat3[0, 2] = n1n3_one_cos + n2sin
    output_mat3[1, 2] = n2n3_one_cos - n1sin
    output_mat3[2, 2] = cos + (n3 * n3 * one_cos)


def compute_transform(position: tuple, rotation_rad: float):
    sin = np.sin(rotation_rad)
    cos = np.cos(rotation_rad)

    return np.asarray([[cos, -sin, position[0]],
                       [sin, cos, position[1]],
                       [0, 0, 1]])


def slerp_mat3(mat3_a, mat3_b, t_value):

    """
    This function creates a rotation transform hat is the spherical linear interpolation between two
    rotation matrices

    :param mat3_a: ndarray (3, 3) <np.float32>
    :param mat3_b: ndarray (3, 3) <np.float32>
    :param output_mat3: ndarray (3, 3) <np.float32>
    :return:
    """

    # TODO: Create array version of this where memory won't be re-allocated every time
    quat_a = np.ndarray((4, ), dtype=np.float32)
    quat_b = np.ndarray((4, ), dtype=np.float32)
    output_mat3 = np.ndarray((3, 3), dtype=np.float32)

    quaternion.mat3_to_quat(mat3_a, quat_a)
    quaternion.mat3_to_quat(mat3_b, quat_b)
    quat_c = quaternion.slerp_quat(quat_a, quat_b, t_value)
    quaternion.quat_to_mat3(quat_c, output_mat3)

    return output_mat3


def euler(x_rad=0, y_rad=0, z_rad=0, order='xyz'):

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

    cx = np.cos(x_rad)
    sx = np.sin(x_rad)
    cy = np.cos(y_rad)
    sy = np.sin(y_rad)
    cz = np.cos(z_rad)
    sz = np.sin(z_rad)

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

    return rotation

from numba import njit
import numpy as np
from scipy.spatial.transform import Rotation

SLERP_DOT_THRESHOLD = 0.9995


def multi_euler_to_quaternion(euler_angles: np.ndarray, rotation_orders: list):
    """
    [NOTE] Function originaly written by ChatGPT4 and modified by me
    Convert Euler angles to quaternions.

    :param euler_angles: (N, 3) array of Euler angles.
    :param rotation_orders: (N,) array of integers representing rotation orders.
    :return: (N, 4) array of quaternions.
    """
    # Map integer rotation orders to the corresponding string representations
    order_mapping = {0: 'xyz', 1: 'zyx', 2: 'yxz', 3: 'xzy', 4: 'zxy', 5: 'yzx'}
    quaternions = np.empty((len(euler_angles), 4), dtype=np.float32)

    # Convert each set of Euler angles to a quaternion
    for i, (angles, order) in enumerate(zip(euler_angles, rotation_orders)):
        rotation_order = order_mapping.get(order, 'xyz')  # Default to 'xyz' if not found
        rotation = Rotation.from_euler(rotation_order, angles, degrees=False)
        quaternions[i] = rotation.as_quat()

    return quaternions


@njit
def mat3_to_quat(mat3, output_quat):
    """
    [ Robust method ]
    This is the robust version of the method described in:
    https://www.euclideanspace.com/maths/geometry/rotations/conversions/matrixToQuaternion/

    :param mat: numpy array (3, 3) <np.float32>
    :param output_quat: numpy array (4,) <np.float32> [w, x, y, z]
    """

    trace = np.trace(mat3)  # Trace is the sum of diagonal elements
    if trace > 0:
        S = np.sqrt(trace + 1.0) * 2
        output_quat[0] = 0.25 * S
        output_quat[1] = (mat3[2, 1] - mat3[1, 2]) / S
        output_quat[2] = (mat3[0, 2] - mat3[2, 0]) / S
        output_quat[3] = (mat3[1, 0] - mat3[0, 1]) / S
    elif mat3[0, 0] > mat3[1, 1] and mat3[0, 0] > mat3[2, 2]:
        S = np.sqrt(1.0 + mat3[0, 0] - mat3[1, 1] - mat3[2, 2]) * 2
        output_quat[0] = (mat3[2, 1] - mat3[1, 2]) / S
        output_quat[1] = 0.25 * S
        output_quat[2] = (mat3[0, 1] + mat3[1, 0]) / S
        output_quat[3] = (mat3[0, 2] + mat3[2, 0]) / S
    elif mat3[1, 1] > mat3[2, 2]:
        S = np.sqrt(1.0 + mat3[1, 1] - mat3[0, 0] - mat3[2, 2]) * 2
        output_quat[0] = (mat3[0, 2] - mat3[2, 0]) / S
        output_quat[1] = (mat3[0, 1] + mat3[1, 0]) / S
        output_quat[2] = 0.25 * S
        output_quat[3] = (mat3[1, 2] + mat3[2, 1]) / S
    else:
        S = np.sqrt(1.0 + mat3[2, 2] - mat3[0, 0] - mat3[1, 1]) * 2
        output_quat[0] = (mat3[1, 0] - mat3[0, 1]) / S
        output_quat[1] = (mat3[0, 2] + mat3[2, 0]) / S
        output_quat[2] = (mat3[1, 2] + mat3[2, 1]) / S
        output_quat[3] = 0.25 * S


@njit
def quat_to_mat3(quat, output_mat3):

    """
    Converts a (4,) quaternionvector in to (3, 3) rotation matrix
    Formula from: http://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToMatrix/index.htm
    :param q_vector: (4,) in order [w, x, y, z]
    :return:
    """

    qw = quat[0]
    qx = quat[1]
    qy = quat[2]
    qz = quat[3]

    output_mat3[0, 0] = 1 - 2 * qy * qy - 2 * qz * qz
    output_mat3[1, 0] = 2 * qx * qy + 2 * qz * qw
    output_mat3[2, 0] = 2 * qx * qz - 2 * qy * qw

    output_mat3[0, 1] = 2 * qx * qy - 2 * qz * qw
    output_mat3[1, 1] = 1 - 2 * qx * qx - 2 * qz * qz
    output_mat3[2, 1] = 2 * qy * qz + 2 * qx * qw

    output_mat3[0, 2] = 2 * qx * qz + 2 * qy * qw
    output_mat3[1, 2] = 2 * qy * qz - 2 * qx * qw
    output_mat3[2, 2] = 1 - 2 * qx * qx - 2 * qy * qy


@njit
def slerp_quat(quat_a, quat_b, t_value):

    """
    Performs the spherical interpolation of two quaternions.
    Original code modified from:

    https://en.wikipedia.org/wiki/Slerp

    :param quat_a: numpy array (4,) [w, x, y, z] <np.float32>
    :param quat_b: numpy array (4,) [w, x, y, z] <np.float32>
    :param t_value: float
    :param output_quat: numpy array (4,) [w, x, y, z] <np.float32>
    """

    dot = np.sum(quat_a * quat_b)

    if dot < 0.0:
        quat_b = -quat_b
        dot = -dot

    # If the dot is too close to singularity, just linearly interpolate them
    if dot > SLERP_DOT_THRESHOLD:

        output_quat = quat_a + t_value * (quat_b - quat_a)
        output_quat /= np.linalg.norm(output_quat)

    else:

        theta_0 = np.arccos(dot)
        sin_theta_0 = np.sin(theta_0)

        theta = theta_0 * t_value
        sin_theta = np.sin(theta)

        s0 = np.cos(theta) - dot * sin_theta / sin_theta_0
        s1 = sin_theta / sin_theta_0
        output_quat = (s0 * quat_a) + (s1 * quat_b)

    return output_quat

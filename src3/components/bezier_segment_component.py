import numpy as np

from glm import vec3, vec4, mat3, mat4, mat3x4, mat4x3, normalize, rotate
from src3 import constants


class BezierSegmentComponent:
    """
    The Bezier segment is a unit of a bezier curve that allows you to interpolate points on one cubic spline.
    There are four 3D control points and two twists controls for rotation along the bezier segment (begining and end)
    """

    def __init__(self, control_points=None,
                 num_segments=32,
                 start_twist_angle=0.0,
                 stop_twist_angle=0.0):

        """
        :param control_points: ndarray (4, 3) <np.float32>
        """

        # Control points are absolute values! Forget about the blender handles!
        if control_points is None:
            self.control_points = np.array([[0, 0, 0],
                                            [0.3333, 0, 0],
                                            [0.6667, 0, 0],
                                            [1.0, 0, 0]], dtype=np.float32)
        elif type(control_points) is np.ndarray:
            if control_points.shape == (4, 3):
                self.control_points = control_points.copy()  # Numpy nd array
            else:
                raise Exception("[ERROR] Provided 'control_point' doesn#t match shape (4, 3)")

        self.num_segments = num_segments
        self.start_twist_angle = start_twist_angle
        self.stop_twist_angle = stop_twist_angle

    def generate_vbos_and_vaos(self):
        pass

    def render(self):
        pass

    def interpolate_single_point(self, t_value):

        """
        Simple demo function used to get a single point. Do not use this for an array of points.
        :param t_value: float
        :return:
        """

        t_matrix = np.empty((1, 4), dtype=np.float32)
        t_matrix[:, 0] = t_value ** 3
        t_matrix[:, 1] = t_value ** 2
        t_matrix[:, 2] = t_value
        t_matrix[:, 3] = 1

        return np.matmul(t_matrix, np.matmul(constants.BEZIER_COEFFS, self.control_points))

    def interpolate_points(self, t_values):

        """
        Returns the respective points for each of the t_values
        :param t_values: numpy array (n, ) <np.float32>
        :return:
        """

        t_matrix = np.empty((t_values.size, 4), dtype=np.float32)
        t_matrix[:, 0] = t_values ** 3
        t_matrix[:, 1] = t_values ** 2
        t_matrix[:, 2] = t_values
        t_matrix[:, 3] = 1

        return np.matmul(t_matrix, np.matmul(constants.BEZIER_COEFFS, self.control_points))

    def interpolate_tangents(self, t_values, normalize=True):

        """
        Returns the respective points for each of the t_values
        :param t_values: numpy array (n, ) <np.float32>
        :return:
        """

        t_matrix = np.empty((t_values.size, 4), dtype=np.float32)
        t_matrix[:, 0] = 3 * (t_values ** 2)
        t_matrix[:, 1] = 2 * t_values
        t_matrix[:, 2] = 1
        t_matrix[:, 3] = 0

        tangents = np.matmul(t_matrix, np.matmul(constants.BEZIER_COEFFS, self.control_points))

        if normalize:
            return (tangents.T / np.linalg.norm(tangents, axis=1)).T
        else:
            return tangents

    def interpolate_rotations_mat3(self, t_values, rotation_start, rotation_stop, up_vector_start=None):

        if t_values.size < 2:
            raise Exception('[ERROR] You need at least 2 t_values to interpolate functions')

        # If no up_vector_start is defined, use Y-Axis as default
        if up_vector_start is None:
            up_vector_start = np.array([0, 1, 0], dtype=np.float32)

        # Setup
        tangents = self.interpolate_tangents(t_values=t_values, normalize=True)
        rotations_mat3 = np.zeros((t_values.size, 3, 3), dtype=np.float32)
        previous_up_vector = up_vector_start
        angles = np.linspace(rotation_start, rotation_stop, t_values.size)
        angle_increment = np.diff(angles, prepend=[0])
        temp_rotation = np.ndarray((3, 3), dtype=np.float32)

        # Create transforms
        for i in range(t_values.size):
            mat3.look_at_direction(direction=tangents[i, :],
                                   up_vector=previous_up_vector,
                                   output_mat3=rotations_mat3[i, :, :])

            # [ Apply Axis Rotation ]
            mat3.rotate_around_vector(tangents[i, :], angle_increment[i], temp_rotation)
            rotations_mat3[i, :, :] = np.matmul(temp_rotation, rotations_mat3[i, :, :])
            previous_up_vector = rotations_mat3[i, :, 1]

        return rotations_mat3

    def interpolate_transforms_mat4(self, t_values, rotation_start, rotation_stop, up_vector_start=None):

        """
        This function create a series of 3D transforms as 4x4 matrices along the bezier curve based on the
        direction of initial up vector and the initial/final rotation
        :param t_values: numpy array (n, ) <np.float32>
        :param up_vector_start: 3D vector showing UP. numpy array (3, ) <np.float32>
        :param rotation_start: float
        :param rotation_stop: float
        :return:
        """

        transforms_mat4 = np.zeros((t_values.size, 4, 4), dtype=np.float32)
        transforms_mat4[:, 0:3, 0:3] = self.interpolate_rotations_mat3(t_values=t_values,
                                                                       rotation_start=rotation_start,
                                                                       rotation_stop=rotation_stop,
                                                                       up_vector_start=up_vector_start)
        transforms_mat4[:, 0:3, 3] = self.interpolate_points(t_values=t_values)
        transforms_mat4[:, 3, 3] = 1.0

        return transforms_mat4

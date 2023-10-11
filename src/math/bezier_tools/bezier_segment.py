import numpy as np
import obsolete_code.bezier_tools.default as default
from obsolete_code.math_utils import mat3

BEZIER_COEFFS_INV = np.linalg.inv(default.BEZIER_COEFFS)

class BezierSegment:

    """
    The Bezier segment is a unit of a bezier curve that allows you to interpolate points on one bicubic spline.
    There are four 3D control points and two twists controls for rotation along the bezier segment (begining and end)
    """

    def __init__(self, control_points=None,
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

        self.start_twist_angle = start_twist_angle
        self.stop_twist_angle = stop_twist_angle

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

        return np.matmul(t_matrix, np.matmul(default.BEZIER_COEFFS, self.control_points))

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

        return np.matmul(t_matrix, np.matmul(default.BEZIER_COEFFS, self.control_points))

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

        tangents = np.matmul(t_matrix, np.matmul(default.BEZIER_COEFFS, self.control_points))

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

    def fit_to_points_ls(self, points, lock_end_points=False):

        # Following the method described in : https://pomax.github.io/bezierinfo/#curvefitting
        # Which is based on: https://web.archive.org/web/20180403213813/http://jimherold.com/2012/04/20/least-squares-bezier-fit/

        # Step 1) Estimate t values for points
        points_diff = np.diff(points, axis=0)
        distances = np.linalg.norm(points_diff, axis=1)
        total_dist = np.sum(distances)
        t_points = np.zeros(points.shape[0], dtype=np.float32)
        t_points[1:] = np.cumsum(distances) / total_dist

        # Step 2) Update control points with initial guess
        tan_1 = points[1, :] - points[0, :]
        tan_1 /= np.linalg.norm(tan_1)
        tan_2 = points[2, :] - points[3, :]
        tan_2 /= np.linalg.norm(tan_2)

        # Step 2) Create T matrix for predictions
        t_matrix = np.empty((t_points.size, 4), dtype=np.float32)
        t_matrix[:, 0] = t_points ** 3
        t_matrix[:, 1] = t_points ** 2
        t_matrix[:, 2] = t_points
        t_matrix[:, 3] = 1

        # Step 3) Solve all dimensions using least-squares
        new_control_points = BEZIER_COEFFS_INV @ np.linalg.pinv(t_matrix) @ points

        if lock_end_points:
            new_control_points[0, :] = points[0, :]
            new_control_points[3, :] = points[-1, :]

    def fit_to_points(self, points, num_iterations=4):

        def normalize(vector, length=1):
            current = np.linalg.norm(vector)
            scale = length / current if current != 0 else 0
            return vector * scale

        epsilon = 1E-6

        # Calculate the relative relative t of each point if they were projected on curve
        points_diff = np.diff(points, axis=0)
        distances = np.linalg.norm(points_diff, axis=1)
        total_dist = np.sum(distances)
        u_prime = np.zeros(points.shape[0], dtype=np.float32)
        u_prime[1:] = np.cumsum(distances) / total_dist

        # Calculate first and last tangents
        tan_1 = points[1, :] - points[0, :]
        tan_1 /= np.linalg.norm(tan_1)
        tan_2 = points[-2, :] - points[-1, :]
        tan_2 /= np.linalg.norm(tan_2)

        # ======= Adaptation of the Graphics Gems algorithm =====

        pt_1 = points[0, :]
        pt_2 = points[-1, :]

        C = np.zeros((2, 2), dtype=np.float32)
        X = np.array([0, 0], dtype=np.float32)

        for i, point in enumerate(points):
            u = u_prime[i]
            t = 1.0 - u
            b = 3 * u * t
            b0 = t * t * t
            b1 = b * t
            b2 = b * u
            b3 = u * u * u

            a1 = normalize(tan_1, b1)
            a2 = normalize(tan_2, b2)
            tmp = point - pt_1 * (b0 + b1) - pt_2 * (b2 + b3)
            C[0, 0] += np.dot(a1, a1)
            C[0, 1] += np.dot(a1, a2)
            C[1, 0] = C[0, 1]  # Move this outside of the loop
            C[1, 1] += np.dot(a2, a2)
            X[0] += np.dot(a1, tmp)
            X[1] += np.dot(a2, tmp)

        # Compute the determinants of C and X
        detC0C1 = C[0, 0] * C[1, 1] - C[1, 0] * C[0, 1]
        if np.abs(detC0C1) > epsilon:
            # Kramer's rule
            detC0X = C[0, 0] * X[1] - C[1, 0] * X[0]
            detXC1 = X[0] * C[1, 1] - X[1] * C[0, 1]
            # Derive alpha values
            alpha_1 = detXC1 / detC0C1
            alpha_2 = detC0X / detC0C1
        else:
            # Matrix is under-determined, try assuming alpha_1 == alpha_2
            c0 = C[0, 0] + C[0, 1]
            c1 = C[1, 0] + C[1, 1]
            if np.abs(c0) > epsilon:
                alpha_1 = alpha_2 = X[0] / c0
            elif np.abs(c1) > epsilon:
                alpha_1 = alpha_2 = X[1] / c1
            else:
                # Handle below
                alpha_1 = alpha_2 = 0

        segLength = np.linalg.norm(pt_2 - pt_1)
        epsilon *= segLength
        if alpha_1 < epsilon or alpha_2 < epsilon:
            # fall back on standard (probably inaccurate) formula,
            # and subdivide further if needed.
            alpha_1 = alpha_2 = segLength / 3

        # update control points
        self.control_points[0, :] = pt_1
        self.control_points[1, :] = pt_1 + normalize(tan_1, alpha_1)
        self.control_points[2, :] = pt_2 + normalize(tan_2, alpha_2)
        self.control_points[3, :] = pt_2
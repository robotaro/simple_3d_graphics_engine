import numpy as np
from obsolete_code.bezier_tools.bezier_segment import BezierSegment
import h5py

class BezierCurve:

    """
    A bezier curve is composed of different bezier segments in order to represent a more complex curve.
    """

    def __init__(self, control_points=None):

        self.segments = []  # list of ndarray (4, 3) np.float32
        if type(control_points) == list:

            for cp in control_points:
                if cp != np.ndarray:
                    raise Exception('[ERROR] All items in the list must be a numpy array')
                if cp.shape != (4, 3):
                    raise Exception('[ERROR] All arrays in the list must be have shape (4, 3)')
                self.segments.append(BezierSegment(control_points=control_points))
            pass
        elif control_points == np.ndarray:
            if control_points.shape != (4, 3):
                raise Exception('[ERROR] All arrays in the list must be have shape (4, 3)')
            self.segments.append(control_points)
        elif control_points == None:
            new_cp =  np.array([[0, 0, 0],
                                [0.3333, 0, 0],
                                [0.6667, 0, 0],
                                [1.0, 0, 0]], dtype=np.float32)
            self.segments.append(BezierSegment(new_cp))
        else:
            raise Exception('[ERROR] Format not supported')

        self.segments = []  # list of BezierSegments
        self.num_transform_per_segment = 8

    def load_from_h5(self, h5_fpath):

        """
        This function loads the bezier curve from a list of
         [group: BEZIER_CURVE_NAME]
            [attr: 'type': 'bezier_curve']
            [dataset: 'control_points'] (n, 4) <float32>

        n = number of bezier segments

        """

        h5_file = h5py.File(h5_fpath, 'r')

        print('[Loading Bezier Patches]')
        for i, key in enumerate(list(h5_file.keys())):
            print(f" > {i + 1}/{len(h5_file.keys())}", end='')

            if h5_file[key].attrs['type'] != 'bezier_curve':
                print(' Not a bezier curve, skipping.')
                continue

            # Go through each segment
            for j in range(h5_file[key]['segments'].shape[0]):

                new_segment = BezierSegment(control_points=h5_file[key]['segments'][j, :, :])
                self.segments.append(new_segment)

            print(' OK')

        h5_file.close()

    def interpolate_points(self, t_values) -> np.ndarray:

        """
        Interpolates values across the entire length of the curve, which is made by one or more segments.
        TODO: Add 'euclidian_distance' option in order to eclidiand spaceing along the curve, rather than in
              non-euclidian t-space
        # WARNING: All t_values must be in ASCENDING ORDER
        :param t_values:
        :return:
        """

        if type(t_values) == float or type(t_values) == int or type(t_values) == np.float32:
            t_values = np.array([t_values], dtype=np.float32)

        # Determine which segment the t_value falls into
        segment_length = 1.0 / len(self.segments)
        t_value_segment_indices = (t_values / segment_length).astype(np.int32)

        points = np.ndarray((t_values.size, 3), dtype=np.float32)
        counter = 0
        for i, segment in enumerate(self.segments):

            selected_t_value_indices = np.where(t_value_segment_indices == i)[0]
            a = counter
            b = a + selected_t_value_indices.size
            segment_t_values = (t_values[selected_t_value_indices] - i * segment_length) / segment_length
            points[a:b, :] = segment.interpolate_points(t_values=segment_t_values)
            counter = b

        # last point if any TODO: Remove code repetition
        selected_t_value_indices = np.where(t_value_segment_indices == len(self.segments))[0]
        if selected_t_value_indices.size > 0:
            segment_t_values = (t_values[selected_t_value_indices] - i * segment_length) / segment_length
            points[counter:, :] = self.segments[-1].interpolate_points(t_values=segment_t_values)

        return points

    def interpolate_rotations_mat3(self, t_values, rotation_start, rotation_stop, up_vector_start=None):



        pass

    def bake_length(self) -> None:

        """
        Aproximates the t_values to their actual euclidean length
        :return:
        """
        pass

    def create_circle(self, center=np.ndarray([0, 0], dtype=np.float32), radius=1.0) -> None:

        """
        This is a demo function that initializes the curve as a closed circle.
        The mathematical explanation for the circle can be found in:
        https://spencermortensen.com/articles/bezier-circle/

        :param center:
        :param radius:
        :return:
        """

        # Circle constant
        c = 0.551915024494

        # Create 4 sets of 4 control points with 3 dimensions each
        segments_cp = np.ndarray((4, 4, 3), dtype=np.float32)
        segments_cp[0, :] = [[0, 0, 1], [c, 0, 1], [1, 0, c], [1, 0, 0]]
        segments_cp[1, :] = [[1, 0, 0], [1, 0, -c], [c, 0, -1], [0, 0, -1]]
        segments_cp[2, :] = [[0, 0, -1], [-c, 0, -1], [-1, 0, -c], [-1, 0, 0]]
        segments_cp[3, :] = [[-1, 0, 0], [-1, 0, c], [-c, 0, 1], [0, 0, 1]]

        # Add all segments to the list of segments
        for i in range(segments_cp.shape[0]):
            new_segment = BezierSegment()
            new_segment.control_points = segments_cp[i, :, :]
            self.segments.append(new_segment)
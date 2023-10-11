import numpy as np

from obsolete_code.bezier_tools.regular_quad_patch import RegularQuadPatch
import obsolete_code.bezier_tools.default as default


class BezierPatch:

    """
    The Bezier Patch class can create and modify a 3D bucubic bezier surface
    """

    def __init__(self, control_points=None):

        if type(control_points) is np.ndarray:
            if not np.equal(control_points.shape, (4, 4, 3)):
                raise Exception(f'[ERROR] Control points must have shaoe (4, 4, 3)')
            self.control_points = control_points
        elif control_points is None:
            # Setup empty points
            self.control_points = np.ndarray((4, 4, 3), dtype=np.float32)
        else:
            raise Exception(f'[ERROR] Non-suported type {type(control_points)}')

        self.adjacent_patches = [None for i in range(max(default.PATCH_EDGE_LIST) + 1)]

    def get_corner_control_points(self, corner_id):

        row = default.PATCH_CORNER_COORDS[corner_id, 0]
        col = default.PATCH_CORNER_COORDS[corner_id, 1]
        return self.control_points[row, col, :]

    def set_corner_control_points(self, corner_id, control_points):

        row = default.PATCH_CORNER_COORDS[corner_id, 0]
        col = default.PATCH_CORNER_COORDS[corner_id, 1]
        self.control_points[row, col, :] = control_points

    def get_edge_control_points(self, edge_id):

        """

        [WARNING] BOTTON and LEFT edges are reversed in order for all edge to follow
                  in the counter(anti) clockwise order!
        :param edge_id:
        :return:
        """

        if edge_id == default.PATCH_TOP_EDGE:
            return self.control_points[0, :, :]

        if edge_id == default.PATCH_RIGHT_EDGE:
            return self.control_points[:, -1, :]

        if edge_id == default.PATCH_BOTTOM_EDGE:
            return self.control_points[-1, :, :][::-1, :]  # Inverted to follow anti-clockwise pattern

        if edge_id == default.PATCH_LEFT_EDGE:
            return self.control_points[:, 0, :][::-1, :]  # Inverted to follow anti-clockwise pattern

    def set_edge_control_points(self, edge_id, edge_control_points):

        """
        [WARNING] BOTTON and LEFT edges are expected to be provided "reversed", I.E., as if the edge pattern
                  was counter(anti) clock-si

        :param edge_control_points: ndarray (4, 3)
        :return:
        """

        if edge_id == default.PATCH_TOP_EDGE:
            self.control_points[0, :, :] = edge_control_points

        if edge_id == default.PATCH_RIGHT_EDGE:
            self.control_points[:, -1, :] = edge_control_points

        if edge_id == default.PATCH_BOTTOM_EDGE:
            self.control_points[-1, :, :] = edge_control_points[::-1, :]

        if edge_id == default.PATCH_LEFT_EDGE:
            self.control_points[:, 0, :] = edge_control_points[::-1, :]

    def get_adjacent_patch(self, edge_id):

        """
        It will return the reference to the patch adjacent to this by the specified edge_id, and the
        edge on the adjacent patch that is connected to this one. Given that the patches may be rotated,
        using the opposite edge will not all always work
        :param edge_id: int
        :return: (adj_patch, adj_patch_edge_id) or None, -1
        """

        adj_patch = self.adjacent_patches[edge_id]
        if adj_patch is None:
            return None, -1
        else:
            for i, test_edge_id in enumerate(default.PATCH_EDGE_LIST):
                reflected_patch = adj_patch.adjacent_patches[test_edge_id]
                if reflected_patch == self:
                    return adj_patch, test_edge_id
            return None, -1

    def from_regular_quad_patch(self, regular_quad_patch):

        """

        This function takes a quad_patch and fits a bezier surface to it. The quad_patch is defined as a 2D array
        where each element is a vertex. Edge cases are when num_rows or num_cols are equal to 1 or 2. For N, it uses the
        implementation described in:
        "MA 323 Geometric Modelling / Course Notes: Day 28 / Data Fitting to Surfaces"

        :param regular_quad_patch: dictionary with format:
                {'indices': ndarray (num_rows, num_cols) <int32>,  # Blender indices, or any global indexing system
                 'vertices': ndarray (num_rows, num_cols, 3) <float32>
                 'normals': ndarray (num_rows, num_cols, 3) <float32> }
        :return:
        """

        if type(regular_quad_patch) is not RegularQuadPatch:
            raise Exception('f[ERROR] Type {type(quad_patch)} not supported')

        (num_rows, num_cols) = regular_quad_patch.indices.shape

        vertices = regular_quad_patch.vertices

        if num_rows == 2:
            # If there are only two points, interpolate two more
            new_vertices = np.ndarray((4, num_cols, 3), dtype=np.float32)
            new_vertices[0, :, :] = regular_quad_patch.vertices[0, :, :]
            new_vertices[3, :, :] = regular_quad_patch.vertices[1, :, :]

            vectors = new_vertices[3, :, :] - new_vertices[0, :, :]
            new_vertices[1, :, :] = vectors * 0.333333 + new_vertices[0, :, :]
            new_vertices[2, :, :] = vectors * 0.666666 + new_vertices[0, :, :]
            vertices = new_vertices
            num_rows = 4

        #elif num_rows == 3:
        #    print('[WARNING] Quad patch has 3 rows. Edge case?')

        if num_cols == 2:
            # If there are only two points, interpolate two more
            new_vertices = np.ndarray((num_rows, 4, 3), dtype=np.float32)
            new_vertices[:, 0, :] = regular_quad_patch.vertices[:, 0, :]
            new_vertices[:, 3, :] = regular_quad_patch.vertices[:, 1, :]

            vectors = new_vertices[:, 3, :] - new_vertices[:, 0, :]
            new_vertices[:, 1, :] = vectors * 0.333333 + new_vertices[:, 0, :]
            new_vertices[:, 2, :] = vectors * 0.666666 + new_vertices[:, 0, :]
            vertices = new_vertices
            num_cols = 4

        #elif num_cols == 3:
        #    print('[WARNING] Quad patch has 3 columns. Edge case?')

        # TODO: Test if we can improve t-value estimation by using euclidian distances
        # Step 1) Approximate t spacing using the distances between vertices
        # dist_u = np.linalg.norm(np.diff(vertices, axis=0), axis=2)
        # t_u = np.zeros((num_rows, num_cols), dtype=np.float32)
        # t_u[1:, :] = np.cumsum(dist_u, axis=0) / np.sum(dist_u, axis=0)

        t_u = np.linspace(0, 1, num_rows)
        T_u = np.empty((4, t_u.size), dtype=np.float32)
        T_u[0, :] = t_u ** 3
        T_u[1, :] = t_u ** 2
        T_u[2, :] = t_u
        T_u[3, :] = 1
        U = default.BEZIER_COEFFS @ T_u
        U_inv = np.linalg.pinv(U)

        t_v = np.linspace(0, 1, num_cols)
        T_v = np.empty((4, t_v.size), dtype=np.float32)
        T_v[0, :] = t_v ** 3
        T_v[1, :] = t_v ** 2
        T_v[2, :] = t_v
        T_v[3, :] = 1
        V = default.BEZIER_COEFFS @ T_v
        V_inv = np.linalg.pinv(V)

        self.control_points = np.ndarray((4, 4, 3), dtype=np.float32)
        for i in range(vertices.shape[2]):
            self.control_points[:, :, i] = U_inv.T @ vertices[:, :, i] @ V_inv

        return self.control_points

    def to_regular_quat_patch(self, segments_u, segments_v, calc_normals_using_quads=True):

        if segments_u < 1:
            segments_u = 1
        if segments_v < 1:
            segments_v = 1

        size_u = segments_u + 1
        size_v = segments_v + 1

        t_u = np.linspace(0, 1, size_u)
        T_u = np.empty((4, t_u.size), dtype=np.float32)
        T_u[0, :] = t_u ** 3
        T_u[1, :] = t_u ** 2
        T_u[2, :] = t_u
        T_u[3, :] = 1
        U = default.BEZIER_COEFFS @ T_u

        t_v = np.linspace(0, 1, size_v)
        T_v = np.empty((4, t_v.size), dtype=np.float32)
        T_v[0, :] = t_v ** 3
        T_v[1, :] = t_v ** 2
        T_v[2, :] = t_v
        T_v[3, :] = 1
        V = default.BEZIER_COEFFS @ T_v

        # Create output regular quat patch - indices are not initialized!
        new_regular_quad_patch = RegularQuadPatch()
        new_regular_quad_patch.indices = np.ones((size_u, size_v), dtype=np.int32) * -1
        new_regular_quad_patch.vertices = np.ndarray((size_u, size_v, 3), dtype=np.float32)
        new_regular_quad_patch.normals = np.ndarray((size_u, size_v, 3), dtype=np.float32)

        # Calculate vertices
        for i in range(self.control_points.shape[2]):
            # X = P^t @ P @ V
            new_regular_quad_patch.vertices[:, :, i] = U.T @ self.control_points[:, :, i] @ V

        # Calculate normals
        if calc_normals_using_quads:

            # The quad method is simple: We calculate the

            # TODO: Re-do all this
            #   - Slow implementation. Use Numba
            #   - Code repetition!
            for i in range(segments_u):
                for j in range(segments_v):
                    index = i * size_v + j
                    vec_a = new_regular_quad_patch.vertices[i + 1, j, :] - new_regular_quad_patch.vertices[i, j, :]
                    vec_b = new_regular_quad_patch.vertices[i, j + 1, :] - new_regular_quad_patch.vertices[i, j, :]
                    normal = np.cross(vec_a, vec_b)
                    normal /= np.linalg.norm(normal)
                    new_regular_quad_patch.normals[i, j, :] = normal

            # Last Row
            for j in range(segments_v):
                vec_a = new_regular_quad_patch.vertices[-1, j + 1, :] - new_regular_quad_patch.vertices[-1, j, :]
                vec_b = new_regular_quad_patch.vertices[-2, j, :] - new_regular_quad_patch.vertices[-1, j, :]
                normal = np.cross(vec_a, vec_b)
                normal /= np.linalg.norm(normal)
                new_regular_quad_patch.normals[-1, j, :] = normal

            # last column
            for i in range(segments_u):
                vec_a = new_regular_quad_patch.vertices[i, -2, :] - new_regular_quad_patch.vertices[i, -1, :]
                vec_b = new_regular_quad_patch.vertices[i + 1, -1, :] - new_regular_quad_patch.vertices[i, -1, :]
                normal = np.cross(vec_a, vec_b)
                normal /= np.linalg.norm(normal)
                new_regular_quad_patch.normals[i, -1, :] = normal

            # Last point
            vec_a = new_regular_quad_patch.vertices[-2, -1, :] - new_regular_quad_patch.vertices[-1, -1, :]
            vec_b = new_regular_quad_patch.vertices[-1, -2, :] - new_regular_quad_patch.vertices[-1, -1, :]
            normal = np.cross(vec_a, vec_b)
            normal /= np.linalg.norm(normal)
            new_regular_quad_patch.normals[-1, -1, :] = normal

        else:
            raise Exception('[ERROR] Any normal calculate other than using the quads themselves is not yet implemented')

        return new_regular_quad_patch


import numpy as np
import obsolete_code.bezier_tools.default as default

class RegularQuadPatch:

    def __init__(self):

        """
        'indices': ndarray (num_rows, num_cols) <int32>,  # Blender indices, or any global indexing system
         'vertices': ndarray (num_rows, num_cols, 3) <float32>
         'normals': ndarray (num_rows, num_cols, 3) <float32>

        :param num_rows:
        :param num_cols:
        """

        # Data variables
        self.indices = None
        self.vertices = None
        self.normals = None
        self.selected = False

        self.temp_id = -1  # This variable is to be used only when creating another network from this one

        # Node connectivity variables
        self.adjacent_patches = [None for i in range(max(default.PATCH_EDGE_LIST) + 1)]  # Direct reference to adj patches

    def get_edge_indices(self, edge_id):

        """
        Edges folow the counter/anti clockwise order. The edge sequence is Top->Right->Bottom->Left
        where the first index of an edge is the same is its predecessor's last, and the last index of an edge
        is its successor's first.

        :param edge_id: interger defined in default.py. I will most likely be a number from 0 to 3
        :return:
        """
        if self.indices is None:
            raise Exception('[ERROR] Indices have not been initialized')

        if edge_id == default.PATCH_TOP_EDGE:
            return self.indices[0, :]

        if edge_id == default.PATCH_RIGHT_EDGE:
            return self.indices[:, -1]

        if edge_id == default.PATCH_BOTTOM_EDGE:
            return self.indices[-1, :][::-1]

        if edge_id == default.PATCH_LEFT_EDGE:
            return self.indices[:, 0][::-1]

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

    def is_edge_present(self, edge_indices):

        """
        This function compares the input array of edge indices against every edge array on this matrix and
        returns the ID of the edge if there is a match, or -1 otherwise. Values are sorted internally for
        algorithm simplicity.
        :param edge_indices: numpy array (n, )
        :return: int
        """

        sorted_source = np.sort(edge_indices)

        for edge_id in default.PATCH_EDGE_LIST:
            sorted_target = np.sort(self.get_edge_indices(edge_id=edge_id))
            if sorted_source.size == sorted_target.size:
                if np.all(sorted_source == sorted_target):
                    return edge_id
        return -1

    def get_common_edge(self, quad_patch):

        """
        This function compares references to see if the patch in the adjacemtn map contains the quad_patch being queried
        :param quad_patch:
        :return: valid edge ID if there is a match, or else -1 <int>
        """

        for edge_id in default.PATCH_EDGE_LIST:
            if self.adjacent_patches[edge_id] == quad_patch:
                return edge_id
        return -1

    def get_opposite_common_edge(self, quad_patch):
        """
        This function compares references to see if the patch in the adjacemtn map contains the quad_patch being queried
        :param quad_patch:
        :return: valid edge ID if there is a match, or else -1 <int>
        """

        common_edge_id = self.get_common_edge(quad_patch=quad_patch)

        if common_edge_id == -1:
            return common_edge_id
        else:
            return default.PATCH_EDGE_OPPOSITE_MAP[common_edge_id]

    def create_tri_mesh(self, flip_triangles=False):

        """
        This function converts the vertices stored as a quad_patch as a triangles for rendering

        :param quad_patch:
        :return:
        """

        (num_rows, num_cols, _) = self.vertices.shape

        num_triangles = (num_rows - 1) * (num_cols - 1) * 2
        num_vertices = num_triangles * 3

        vertices = np.ndarray((num_vertices, 3), dtype=np.float32)
        normals = np.ndarray((num_vertices, 3), dtype=np.float32)

        if flip_triangles:
            index_offset = np.array([0, 1, 2, 3, 4, 5], dtype=np.int32)
        else:
            index_offset = np.array([0, 2, 1, 3, 5, 4], dtype=np.int32)

        for i in range(num_rows - 1):
            for j in range(num_cols - 1):

                index = 6 * (i * (num_cols - 1) + j)
                i_next = i + 1
                j_next = j + 1

                # Triangle 1
                vertices[index, :] = self.vertices[i, j, :]
                vertices[index + index_offset[1], :] = self.vertices[i, j_next, :]
                vertices[index + index_offset[2], :] = self.vertices[i_next, j, :]

                normals[index, :] = self.normals[i, j, :]
                normals[index + index_offset[1], :] = self.normals[i, j_next, :]
                normals[index + index_offset[2], :] = self.normals[i_next, j, :]

                # Triangle 2
                vertices[index + index_offset[3], :] = self.vertices[i_next, j, :]
                vertices[index + index_offset[4], :] = self.vertices[i, j_next, :]
                vertices[index + index_offset[5], :] = self.vertices[i_next, j_next, :]

                normals[index + index_offset[3], :] = self.normals[i_next, j, :]
                normals[index + index_offset[4], :] = self.normals[i, j_next, :]
                normals[index + index_offset[5], :] = self.normals[i_next, j_next, :]

        return vertices, normals

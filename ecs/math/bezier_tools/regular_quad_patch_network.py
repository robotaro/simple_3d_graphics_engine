import xml.etree.ElementTree as ET

from io import StringIO
import pandas as pd
import numpy as np
import h5py

import obsolete_code.bezier_tools.default as default
from obsolete_code.bezier_tools.regular_quad_patch import RegularQuadPatch

# For debugging

# ====== [DEPRECATED] Constant =======
TAG_CURVE_NETWORK = 'curvenetwork'
TAG_VERTICES = 'vertices'
TAG_HALF_EDGES = 'halfedges'
TAG_HALF_CHAINS = 'halfchains'
TAG_EDGE_CHAINS = 'edgechains'
TAG_PATCH_FACES = 'patch_faces'
TAG_PATCH_VERTICES = 'patch_vertices'

VERTICES_COLUMNS = ['id', 'halfedge', 'px', 'py', 'pz', 'nx', 'ny', 'nz']
HALF_EDGES_COLUMNS = ['id', 'vertex', 'next', 'prev', 'opposite', 'halfchain', 'is_corner']
HALF_CHAINS_COLUMNS = ['id', 'halfedge_front', 'halfedge_back', 'patch', 'edgechain']
EDGE_CHAINS_COLUMNS = ['id', 'halfchain_0', 'halfchain_1', 'num_subdiv']

class RegularQuadPatchNetwork:

    def __init__(self):

        """
        vertices: <!--id halfedge px py pz nx ny nz-->
        half_edges: <!--id vertex next prev opposite halfchain is_corner-->
        half_chains: <!--id halfchain_0 halfchain_1 num_subdiv-->
        """

        # H5 quad patches variables
        self.patches = []

        # Sketchretopo variables
        self.vertices_df = None
        self.half_edges_df = None
        self.half_chains_df = None
        self.edge_chains_df = None

    def load_quad_patches_from_h5(self, h5_fpath, object_name=''):

        """
        This function will load one series of patches from a h5 file. The structure is as follows
        [group: OBJECT_NAME]
            [group: '0']
                [dataset: 'indices'] (n, m) <int32>
                [dataset: 'vertices'] (n, m, 3) <float32>
                [dataset: 'normals'] (n, m, 3) <float32>
            [group: '1']
                [dataset: 'indices'] (n, m) <int32>
                [dataset: 'vertices'] (n, m, 3) <float32>
                [dataset: 'normals'] (n, m, 3) <float32>
            ...
            [group: '999']
                [dataset: 'indices'] (n, m) <int32>
                [dataset: 'vertices'] (n, m, 3) <float32>
                [dataset: 'normals'] (n, m, 3) <float32>

        [group: OBJECT_NAME_2]
            ...

        NOTE: Indices are the Blender indices, and they are used for stiching the patches together

        :param fpath_h5:
        :return:
        """

        h5_file = h5py.File(h5_fpath, 'r')

        if len(object_name) == 0:
            object_name = list(h5_file.keys())[0]

        if object_name not in list(h5_file.keys()):
            raise Exception(f"[ERROR] Object '{object_name}' is not present in the h5 file")

        object_group = h5_file[object_name]

        print('[Loading Quad Patches]')
        for i, key in enumerate(list(object_group.keys())):

            print(f" > {i+1}/{len(object_group.keys())}")
            quad_patch_group = object_group[key]

            new_regular_quad_patch = RegularQuadPatch()

            new_regular_quad_patch.indices = quad_patch_group['indices'][:]
            new_regular_quad_patch.vertices = quad_patch_group['vertices'][:]
            new_regular_quad_patch.normals = quad_patch_group['normals'][:]

            self.patches.append(new_regular_quad_patch)

    def build_network(self):

        """
        This function modifies all the quad patches list in self.regular_quad_patch_list and add their
        connectivity information
        :return:
        """

        if len(self.patches) == 0:
            raise Exception('[ERROR] List of quad_patches is empty')

        # Constants
        max_num_quads_per_vertex = 6

        # Step 1) Create connection and connection count tables
        patch_indices_list = []
        patch_vertices_list = []
        max_index = -1
        for patch in self.patches:
            current_max_index = np.max(patch.indices)
            if current_max_index > max_index:
                max_index = current_max_index
            patch_indices_list.append(patch.indices)
            patch_vertices_list.append(patch.vertices)

        num_vertices = max_index + 1

        vertex_conns = np.ones((num_vertices, max_num_quads_per_vertex), dtype=np.int32) * -1
        vertex_conns_count = np.zeros((num_vertices, ), dtype=np.int32)
        #debug_vertices = np.ndarray((num_vertices, 3), dtype=np.float32)

        for i, vertex_indices in enumerate(patch_indices_list):
            indices_flat = vertex_indices.flatten()
            col_positions = vertex_conns_count[indices_flat]
            vertex_conns[indices_flat, col_positions] = i
            vertex_conns_count[indices_flat] += 1
            #debug_vertices[indices_flat, :] = np.reshape(patch_vertices_list[i], (-1, 3))

        # Step 2) Find common edges
        #problematic_indices = np.where(vertex_conns_count == 5)[0]
        for i, patch in enumerate(self.patches):

            # For each edge
            for j, adj_patch in enumerate(patch.adjacent_patches):

                if adj_patch is not None:
                    continue

                edge_indices = patch.get_edge_indices(j)
                raw_patch_indices = vertex_conns[edge_indices, :]
                unique_patch_indices = np.unique(raw_patch_indices)
                mask_a = unique_patch_indices != -1
                mask_b = unique_patch_indices != i
                adjancent_patch_indices = np.sort(unique_patch_indices[np.logical_and(mask_a, mask_b)])

                for test_patch_index in adjancent_patch_indices:

                    test_patch = self.patches[test_patch_index]
                    id_match = test_patch.is_edge_present(edge_indices)
                    if id_match != -1:
                        patch.adjacent_patches[j] = test_patch  # If you use "patch", it won't work as None will be a
                                                                # copy, and you will be modifying a copy. Get it?
                        break

    def debug_test_connections(self):

        # Step 1)
        #   - Brand all patches with IDs equal to their respective list indices
        #   - Create a respective bezier curve for that patch
        for i, quad_patch in enumerate(self.patches):
            quad_patch.temp_id = i

        # Step 2) Add connectivity information to the bezier patches
        for i, quad_patch in enumerate(self.patches):
            for j, adj_quad_patch in enumerate(quad_patch.adjacent_patches):
                if adj_quad_patch is not None:
                    index = adj_quad_patch.temp_id
                    self.patches[i].adjacent_patches[j] = self.patches[index]

        print('[DEBUG] Testing quad patch connections')
        for i, patch in enumerate(self.patches):
            print(f'  Patch {i + 1}/{len(self.patches)}')
            for j, edge_id in enumerate(default.PATCH_EDGE_LIST):

                adj_patch = patch.adjacent_patches[edge_id]
                if adj_patch is None:
                    print(f'    > No connection')
                    continue
                else:
                    match = False
                    for k, test_edge_id in enumerate(default.PATCH_EDGE_LIST):
                        reflected_patch = adj_patch.adjacent_patches[test_edge_id]
                        if reflected_patch == patch:
                            match = True  # this edge is the one connected back to the 'patch'
                    if match:
                        print(f'    > OK')
                    else:
                        print(f'    > Wrong')

        # Step 3) Clean up all the temp indices from the quad patche
        for i, quad_patch in enumerate(self.patches):
            quad_patch.temp_id = -1


    def select_all(self):
        for patch in self.patches:
            patch.selected = True

    def deselect_all(self):
        for patch in self.patches:
            patch.selected = False

    def inverset_selection(self):
        for patch in self.patches:
            if patch.selected:
                patch.selected = False
            else:
                patch.selected = True

    def select_loop_from_edge(self, patch_index, edge_id):

        """
        NOTE: So far, Patch ID and Patch index are used interchangeably
        :param patch_index:
        :return:
        """
        first_patch = self.patches[patch_index]

        current_patch = self.patches[patch_index]
        current_edge_id = edge_id
        while current_patch is not None:
            current_patch.selected = True

            next_patch = current_patch.adjacent_patches[current_edge_id]
            if next_patch is None:
                break

            current_edge_id = next_patch.get_opposite_common_edge(current_patch)
            current_patch = next_patch

            # Stop before you enter an infinite loop
            if next_patch == first_patch:
                break

    def get_all_selected_indices(self):

        """
        Return the indices of all patches in the self.patches list. Up to now, all indices are being using as IDs,
        but this may change in the future
        :return:
        """

        selected_patch_indices = []
        for i, patch in enumerate(self.patches):
            if patch.selected:
                selected_patch_indices.append(i)

        return np.array(selected_patch_indices, dtype=np.int32)






# ======================================================================================================================
#                                                    Obsolete code
# ======================================================================================================================

    def load_sketchretopo_xml(self, xml_fpath):
        root = ET.parse(xml_fpath).getroot()

        # all items data
        for elem in root:
            if elem.tag == TAG_CURVE_NETWORK:
                for sub_elem in elem:
                    if sub_elem.tag == TAG_VERTICES:
                        text_data = StringIO(sub_elem.text)
                        self.vertices_df = pd.read_csv(text_data, sep=" ", names=VERTICES_COLUMNS)

                    if sub_elem.tag == TAG_HALF_EDGES:
                        text_data = StringIO(sub_elem.text)
                        self.half_edges_df = pd.read_csv(text_data, sep=" ", names=HALF_EDGES_COLUMNS)

                    if sub_elem.tag == TAG_HALF_CHAINS:
                        text_data = StringIO(sub_elem.text)
                        self.half_chains_df = pd.read_csv(text_data, sep=" ", names=HALF_CHAINS_COLUMNS)

                    if sub_elem.tag == TAG_EDGE_CHAINS:
                        text_data = StringIO(sub_elem.text)
                        self.edge_chains_df = pd.read_csv(text_data, sep=" ", names=EDGE_CHAINS_COLUMNS)

        # Extra step for handling data using internal algorithms
        #num_items = self.vertices_padded_df['id'].max() + 1
        self.vertices_df.set_index('id', drop=True, inplace=True)
        self.half_edges_df.set_index('id', drop=True, inplace=True)
        self.half_chains_df.set_index('id', drop=True, inplace=True)
        self.edge_chains_df.set_index('id', drop=True, inplace=True)

    def debug_get_line_segments(self):

        """
        This function returns a numpy()
        :return:
        """

        max_segment_length = 10000
        half_edge_corners = self.half_edges_df.index[np.where(self.half_edges_df['is_corner'] == 1)[0]]

        corners_mask = self.half_edges_df['is_corner'] == 1
        corner_vertex_indices = self.half_edges_df.loc[corners_mask, 'vertex'].values

        corner_vertices = self.vertices_df.loc[corner_vertex_indices, ['px', 'py', 'pz']].values

        patch_counts = self.half_chains_df['patch'].value_counts()
        patch_unique_indices = patch_counts.index.values
        patch_counts = patch_counts.values
        quad_patch_indices = patch_unique_indices[patch_counts == 4]

        # Separate vertices by half chains
        vertex_groups = []
        unique_half_chain_ids = self.half_edges_df['halfchain'].unique()
        for _id in unique_half_chain_ids:
            vertices_ids = self.half_edges_df[self.half_edges_df['halfchain'] == _id]['vertex']
            vertices = self.vertices_df.loc[vertices_ids, ['px', 'py', 'pz']].values
            new_vertex_group = {'id': _id, 'vertices': vertices}
            vertex_groups.append(new_vertex_group)

        # Different attempt to get complete edges
        for edge_chain_id, edge_chain in self.edge_chains_df.iterrows():
            half_chain_ids = self.half_chains_df[self.half_chains_df['edgechain'] == edge_chain_id].index.values
            vertices = []
            for half_chain_id in half_chain_ids:
                vertices.append(self.half_edges_df[self.half_edges_df['halfchain'] == half_chain_id]['vertex'].values)
            unique_vertices = np.unique(np.vstack(vertices))

        """vertex_groups = []
        for corner in half_edge_corners:
            new_group = []
            first_id = corner
            next = corner
            for i in range(max_segment_length):
                new_group.append(int(next))
                next = self.half_edges_df.loc[next, 'next']
                if next == -1 or next == first_id:
                    break
            vertex_groups.append(new_group)

        # try to determine loops
        next = self.half_edges_df.index[0]

        vertices = self.vertices_df[['px', 'py', 'pz']].to_numpy() * 5"""

        return vertex_groups, corner_vertices

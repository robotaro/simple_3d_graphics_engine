import os
import json
import numpy as np

# Constants
GLTF_MESHES = "meshes"
GLTF_PRIMITIVES = "primitives"
GLTF_NODES = "nodes"
GLTF_ROTATION = "rotation"
GLTF_TRANSLATION = "translation"
GLTF_SCALE = "scale"
GLTF_MATRIX = "matrix"
GLTF_SKIN = "skin"
GLTF_CHILDREN = "children"
GLTF_BUFFERS = "buffers"
GLTF_BYTE_LENGTH = "byteLength"
GLTF_URI = "uri"
GLTF_ACCESSORS = "accessors"
GLTF_BUFFER_VIEWS = "bufferViews"

GLTF_ATTR_POSITION = "POSITION"
GLTF_ATTR_NORMAL = "NORMAL"
GLTF_ATTR_TANGENT = "TANGENT"

GLTF_COMPONENT_TYPE_MAP = {
      5120: np.int8,
      5121: np.uint8,
      5122: np.int16,
      5123: np.uint16,
      5124: np.int32,
      5125: np.uint32,
      5126: np.float32}

GLTF_DATA_SHAPE_MAP = {
    "SCALAR": (1,),
    "VEC2": (2,),
    "VEC3": (3,),
    "VEC4": (4,),
    "MAT2": (2, 2),
    "MAT3": (3, 3),
    "MAT4": (4, 4)}

GLTF_DATA_NUM_ELEMENTS_MAP = {
    "SCALAR": 1,
    "VEC2": 2,
    "VEC3": 3,
    "VEC4": 4,
    "MAT2": 4,
    "MAT3": 9,
    "MAT4": 16}

GLTF_ANIMATION_PATH_MAP = {
    "translation": 0,
    "rotation": 1,
    "scale": 2}

GLTF_INTERPOLATION_MAP = {
    "LINEAR": 0,
    "STEP": 1,
    "CUBICSPLINE": 2}


RENDERING_MODES = {
    0: "points",
    1: "lines",
    2: "line_loop",
    3: "line_strip",
    4: "triangles",
    5: "triangle_strip",
    6: "triangle_fan"
}


class GLTFLoader:

    def __init__(self):
        self.gltf_header = None
        self.gltf_data = None
        self.gltf_dependencies = None

        self.scenes = []

    def load(self, gltf_fpath: str):

        # Then, read it in my own way
        filename = os.path.basename(gltf_fpath)
        _, extension = os.path.splitext(filename)

        # Load Header
        with open(gltf_fpath, "r") as file:
            self.gltf_header = json.load(file)

        # Load binary data
        gltf_dir = os.path.dirname(gltf_fpath)
        bin_fpath = os.path.join(gltf_dir, self.gltf_header[GLTF_BUFFERS][0][GLTF_URI])
        target_bin_data_size = self.gltf_header[GLTF_BUFFERS][0][GLTF_BYTE_LENGTH]

        with open(bin_fpath, "rb") as file:
            self.gltf_data = file.read()

        if target_bin_data_size != len(self.gltf_data):
            raise Exception(f"[ERROR] Loaded GLTF binary data from {bin_fpath} has {len(self.gltf_data)} bytes, "
                            f"but was expected to have {target_bin_data_size} bytes")

        # Load dependencies
        # TODO: Load any textures that are listed in the gltf_hedear
        g = 0

    def read_data(self, accessor: dict):
        """
        This function reads the parts of the binary array in memory (loaded from the .bin file) and re-interprets
        the raw bytes into numpy arrays according to the accessor's specified data parameters.
        :param accessor: dict, loaded directly from the GLTF file
        :return:
        """

        if self.gltf_data is None:
            return None

        buffer_view_index = accessor["bufferView"]
        buffer_view = self.gltf_header["bufferViews"][buffer_view_index]
        offset = buffer_view["byteOffset"]
        length = buffer_view["byteLength"]
        data = self.gltf_data[offset:offset + length]
        data_type = GLTF_COMPONENT_TYPE_MAP[accessor["componentType"]]
        num_columns = GLTF_DATA_NUM_ELEMENTS_MAP[accessor["type"]]

        if num_columns == 1:
            return np.frombuffer(data, dtype=data_type)

        # TODO: If the data are matrices, they need to be transposed because in GLTF the memory is laid out
        #       as COLUMN-MAJOR!

        return np.reshape(np.frombuffer(data, dtype=data_type), (-1, num_columns))

    def get_animation(self, index: int):

        if self.gltf_data is None:
            return None

        animation_header = self.gltf_header["animations"][index]
        all_input_accessors = []
        channels = {"translation": [], "rotation": [], "scale": []}

        # Animation channels
        for channel in animation_header["channels"]:

            sampler = animation_header["samplers"][channel["sampler"]]
            output_accessor = self.gltf_header["accessors"][sampler["output"]]
            channels[channel["target"]["path"]].append(
                {"node_index": channel["target"]["node"],
                 "animation_data": self.read_data(accessor=output_accessor)})

            all_input_accessors.append(self.gltf_header["accessors"][sampler["input"]])

        # Make sure that all animation channels use the same timeline, and if so, only return one
        unique_input_buffer_views = set([accessor["bufferView"] for accessor in all_input_accessors])
        if len(unique_input_buffer_views) != 1:
            raise Exception(f"All animation channels should be taking their timestamps from the same buffer view, "
                            f"and there are {len(unique_input_buffer_views)} sources instead.")

        timestamps = self.read_data(accessor=all_input_accessors[0])

        return channels, timestamps

    def get_nodes(self) -> dict:

        if self.gltf_data is None:
            return None

        # GPT 4
        nodes = []
        for node in self.gltf_header["nodes"]:
            node_data = {
                'name': node.get('name', None),
                'translation': np.array(node.get('translation', [0, 0, 0])),
                'rotation': np.array(node.get('rotation', [0, 0, 0, 1])),
                'scale': np.array(node.get('scale', [1, 1, 1])),
                'matrix': np.array(node.get('matrix', np.eye(4))),
                'children': node.get('children', []),
                'mesh': node.get('mesh', None),
                'skin': node.get('skin', None)
            }
            nodes.append(node_data)

        # Mine
        num_nodes = len(self.gltf_header[GLTF_NODES])
        node_name = []
        node_parent_index = np.ones((num_nodes,), dtype=np.int32) * -1
        node_matrix = np.empty((num_nodes, 4, 4), dtype=np.float32)
        node_translation = np.empty((num_nodes, 3), dtype=np.float32)
        node_rotation_quat = np.empty((num_nodes, 4), dtype=np.float32)
        node_scale = np.empty((num_nodes, 3), dtype=np.float32)

        for current_index, node in enumerate(self.gltf_header[GLTF_NODES]):

            for child_index in node.get("children", []):
                node_parent_index[child_index] = current_index

            node_matrix[current_index, :, :] = np.eye(4, dtype=np.float32)
            if "name" in node:
                # GLTF matrices are COLUMN-MAJOR, hence the transpose at the end
                node_name.append(node["name"])

            if "matrix" in node:
                # GLTF matrices are COLUMN-MAJOR, hence the transpose at the end
                node_matrix[current_index, :, :] = np.reshape(np.array(node["matrix"]), (4, 4)).T

            if "translation" in node:
                node_translation[current_index, :] = np.array(node["translation"])

            if "rotation" in node:
                node_rotation_quat[current_index, :] = np.array(node["rotation"])

            if "scale" in node:
                node_scale[current_index, :] = np.array(node["scale"])

        # TODO: Complete this
        return {

        }

    def get_mesh(self, index: int) -> dict:
        if self.gltf_data is None:
            return None

        meshes = []
        for mesh in self.gltf_header["meshes"]:
            combined_indices = []
            combined_vertices = []
            combined_normals = []
            combined_uvs = []
            vertex_count = 0

            for primitive in mesh["primitives"]:

                # Extract data for each primitive
                indices = self.extract_data_from_accessor(primitive["indices"])
                vertices = self.extract_data_from_accessor(primitive["POSITION"])
                normals = self.extract_data_from_accessor(primitive["NORMAL"])
                uvs = self.extract_data_from_accessor(primitive["TEXCOORD_0"])

                # Adjust indices and concatenate data
                if indices is not None:
                    combined_indices.extend(indices + vertex_count)
                if vertices is not None:
                    combined_vertices.extend(vertices)
                    vertex_count += len(vertices)
                if normals is not None:
                    combined_normals.extend(normals)
                if uvs is not None:
                    combined_uvs.extend(uvs)

            # Store the combined data for the mesh
            meshes.append({
                'name': getattr(mesh, 'name', None),
                'indices': np.array(combined_indices),
                'vertices': np.array(combined_vertices),
                'normals': np.array(combined_normals),
                'uvs': np.array(combined_uvs)
            })

        return meshes

    def get_skins(self):
        if self.gltf_data is None:
            return None

        skins = []
        for skin in self.gltf_header["skins"]:
            joints = skin["joints"]
            inverse_bind_matrices_accessor = self.gltf_header["accessors"][skin["inverseBindMatrices"]]
            inverse_bind_matrices_data = self.read_data(accessor=inverse_bind_matrices_accessor)

            # Convert to a suitable format, e.g., 4x4 matrices
            inverse_bind_matrices = inverse_bind_matrices_data.reshape((-1, 4, 4))

            skin_data = {
                'joints': joints,
                'inverseBindMatrices': inverse_bind_matrices
            }
            skins.append(skin_data)

        return skins

    def extract_data_from_accessor(self, accessor_index):
        if accessor_index is None:
            return None
        accessor = self.gltf.accessors[accessor_index]
        binary_data = self.read_binary_data(accessor.bufferView)
        return np.frombuffer(binary_data, dtype=GLTF_COMPONENT_TYPE_MAP[accessor.componentType])

# Usage
loader = GLTFLoader()
loader.load(r"D:\git_repositories\alexandrepv\simple_3d_graphics_engine\resources\meshes\laiku_from_python.gltf")
animation = loader.get_animation(index=-1)
skins = loader.get_skins()
nodes = loader.get_nodes()
mesh = loader.get_mesh(index=-1)
g = 0
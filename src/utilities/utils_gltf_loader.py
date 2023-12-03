import os
import json
import numpy as np

# DEBUG
import matplotlib.pyplot as plt

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

    __slots__ =[
        "gltf_header",
        "gltf_buffer_view_data",
        "gltf_dependencies",
        "scenes"
    ]

    def __init__(self):
        self.gltf_header = None
        self.gltf_buffer_view_data = []
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
            gltf_data = file.read()
            self.gltf_buffer_view_data = [self.select_data_using_buffer_view(buffer_view=buffer_view,
                                                                             gltf_data=gltf_data)
                                          for buffer_view in self.gltf_header[GLTF_BUFFER_VIEWS]]

        # Load dependencies
        # TODO: Load any textures that are listed in the gltf_hedear

    def get_accessor(self, index: int):

        if self.gltf_header is None:
            return None

        return self.gltf_header["accessors"][index]

    def get_data(self, accessor: dict, validate_data=True):
        """
        This function reads the parts of the binary array in memory (loaded from the .bin file) and re-interprets
        the raw bytes into numpy arrays according to the accessor's specified data parameters.
        :param accessor: dict, loaded directly from the GLTF file
        :return:
        """

        if self.gltf_header is None:
            return None

        buffer_view_data = self.gltf_buffer_view_data[accessor["bufferView"]]
        accessor_offset = accessor["byteOffset"]
        data_shape = GLTF_DATA_SHAPE_MAP[accessor["type"]]
        data_type = GLTF_COMPONENT_TYPE_MAP[accessor["componentType"]]
        data_format_size = GLTF_DATA_NUM_ELEMENTS_MAP[accessor["type"]]
        num_elements = accessor["count"]

        data = np.frombuffer(buffer=buffer_view_data,
                             offset=accessor_offset,
                             count=num_elements * data_format_size,
                             dtype=data_type)

        data_reshaped = data.reshape((-1, *data_shape)) if accessor["type"] != "SCALAR" else data

        if validate_data:
            target_data_min = np.array(accessor["min"], dtype=data_type)
            target_data_max = np.array(accessor["max"], dtype=data_type)

            data_min = np.min(data_reshaped, axis=0).flatten()
            data_max = np.max(data_reshaped, axis=0).flatten()

            if not np.isclose(target_data_min, data_min).all():
                print(f"[WARNING] Minimum values differ from loaded ones for accessor {accessor}")

            if not np.isclose(target_data_max, data_max).all():
                print(f"[WARNING] Maximum values differ from loaded ones for accessor {accessor}")

        if accessor["type"] in ["MAT2", "MAT3", "MAT4"]:
            # Transposing is required for the matrix as they are laid ou COLUMN-MAJOR in bytes, but stored
            # as ROW-MAJOR in the numpy arrays
            data_reshaped = np.transpose(data_reshaped, (0, 2, 1))

        return data_reshaped

    def select_data_using_buffer_view(self, buffer_view: dict, gltf_data: bytes) -> bytes:

        """
        Returns a CONTIGUOUS data array that you can then use your np.frombuffer to extrac tthe data you need
        :param buffer_view:
        :param data:
        :return:
        """

        # Extract buffer view properties
        byte_offset = buffer_view.get("byteOffset", 0)
        byte_length = buffer_view["byteLength"]
        byte_stride = buffer_view.get("byteStride", 0)  # Optional

        # Calculate the starting and ending byte positions in the binary data
        last_byte = byte_offset + byte_length

        if byte_stride == 0:
            # If byteStride is not specified, read all the data in one go
            loaded_data = gltf_data[byte_offset:last_byte]
        else:
            # If byteStride is specified, read data element by element
            num_elements = byte_length // byte_stride
            loaded_data = b''.join(gltf_data[byte_offset + i * byte_stride:byte_offset + (i + 1) * byte_stride]
                                   for i in range(num_elements))

        return loaded_data

    def get_animation(self, index: int):

        if self.gltf_header is None:
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
                 "animation_data": self.get_data(accessor=output_accessor)})

            all_input_accessors.append(self.gltf_header["accessors"][sampler["input"]])

        # Make sure that all animation channels use the same timeline, and if so, only return one
        unique_input_buffer_views = set([accessor["bufferView"] for accessor in all_input_accessors])
        if len(unique_input_buffer_views) != 1:
            raise Exception(f"All animation channels should be taking their timestamps from the same buffer view, "
                            f"and there are {len(unique_input_buffer_views)} sources instead.")

        timestamps = self.get_data(accessor=all_input_accessors[0])

        return channels, timestamps

    def get_nodes(self) -> dict:

        if self.gltf_header is None:
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

    def get_all_meshes(self) -> list:
        if self.gltf_header is None:
            return None

        meshes = []
        for mesh in self.gltf_header["meshes"]:

            new_mesh = []
            for primitive in mesh["primitives"]:
                indices = self.get_data(accessor=self.get_accessor(primitive["indices"]))

                # DEBUG
                #print(primitive["indices"], indices[0:30])

                attributes = {key: self.get_data(accessor=self.get_accessor(primitive["attributes"][key])) for key
                              in primitive["attributes"].keys()}
                new_mesh.append({
                    "indices": indices,
                    "attributes": attributes})

            meshes.append(new_mesh)

        return meshes

    def get_skins(self):
        if self.gltf_header is None:
            return None

        skins = []
        for skin in self.gltf_header["skins"]:
            joints = skin["joints"]
            inverse_bind_matrices_accessor = self.gltf_header["accessors"][skin["inverseBindMatrices"]]
            inverse_bind_matrices_data = self.get_data(accessor=inverse_bind_matrices_accessor)

            # Convert to a suitable format, e.g., 4x4 matrices
            inverse_bind_matrices = inverse_bind_matrices_data.reshape((-1, 4, 4))

            skin_data = {
                'joints': joints,
                'inverseBindMatrices': inverse_bind_matrices
            }
            skins.append(skin_data)

        return skins


# Usage
loader = GLTFLoader()
loader.load(r"D:\git_repositories\alexandrepv\simple_3d_graphics_engine\resources\meshes\BrainStem.gltf")
#loader.load(r"D:\git_repositories\alexandrepv\simple_3d_graphics_engine\resources\meshes\laiku_from_python.gltf")
animation = loader.get_animation(index=-1)
skins = loader.get_skins()
nodes = loader.get_nodes()
meshes = loader.get_all_meshes()
g = 0
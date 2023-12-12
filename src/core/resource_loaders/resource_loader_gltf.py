import numpy as np

from src.core import constants
from src.core.resource_loaders.resource import Resource
from src.core.data_block import DataBlock
from src.core.resource_loaders.resource_loader import ResourceLoader

from src.utilities import utils_gltf_reader


class ResourceLoaderGLTF(ResourceLoader):

    def __init__(self, all_resources: dict):
        super().__init__(all_resources=all_resources)

        self.gltf_reader = None

    def load(self, resource_uid: str, fpath: str) -> bool:
        self.gltf_reader = utils_gltf_reader.GLTFReader()
        self.gltf_reader.load(gltf_fpath=fpath)

        self.__load_mesh_resources(resource_uid=resource_uid)
        self.__load_nodes_resources(resource_uid=resource_uid)
        self.__load_animation_resources(resource_uid=resource_uid)

        return True

    def __load_mesh_resources(self, resource_uid: str):
        for mesh_index, mesh in enumerate(self.gltf_reader.get_all_meshes()):

            new_resource = Resource(resource_type=constants.RESOURCE_TYPE_MESH)
            new_resource.metadata["render_mode"] = mesh["render_mode"]
            mesh_attrs = mesh["attributes"]

            if "indices" in mesh:
                new_resource.data_blocks["indices"] = DataBlock(data=mesh["indices"])

            if "POSITION" in mesh_attrs:
                new_resource.data_blocks["vertices"] = DataBlock(data=mesh_attrs["POSITION"])

            if "NORMAL" in mesh_attrs:
                new_resource.data_blocks["normals"] = DataBlock(data=mesh_attrs["NORMAL"])

            if "JOINTS_0" in mesh_attrs:
                new_resource.data_blocks["bones"] = DataBlock(data=mesh_attrs["JOINTS_0"])

            if "WEIGHTS_0" in mesh_attrs:
                new_resource.data_blocks["weights"] = DataBlock(data=mesh_attrs["WEIGHTS_0"])

            self.all_resources[f"{resource_uid}/mesh_{mesh_index}"] = new_resource

    def __load_nodes_resources(self, resource_uid: str):
        nodes = self.gltf_reader.get_nodes()

        num_nodes = len(nodes)
        max_num_children = max(set(len(node["children_indices"]) for node in nodes))

        # Get (or generate) node names if necessary
        node_names = []
        for node_index, node in enumerate(nodes):
            gltf_node_name = node.get("name", "")
            if len(gltf_node_name) > 0:
                node_names.append(gltf_node_name)
                continue
            node_names.append(f"node_{node_index}")

        new_resource = Resource(resource_type=constants.RESOURCE_TYPE_NODES_GLTF,
                                metadata={"node_names": node_names})

        new_resource.data_blocks["parent_index"] = DataBlock(
            data=np.empty((num_nodes,), dtype=np.int16))

        new_resource.data_blocks["num_children"] = DataBlock(
            data=np.empty((num_nodes,), dtype=np.int16))

        new_resource.data_blocks["children_indices"] = DataBlock(
            data=np.empty((num_nodes, max_num_children), dtype=np.int16))

        new_resource.data_blocks["translation"] = DataBlock(
            data=np.empty((num_nodes, 3), dtype=np.float32),
            metadata={"order": ["x", "y", "z"]})

        new_resource.data_blocks["rotation"] = DataBlock(
            data=np.empty((num_nodes, 4), dtype=np.float32),
            metadata={"order": ["x", "y", "z", "w"], "type": "quaternion"})

        new_resource.data_blocks["scale"] = DataBlock(
            data=np.empty((num_nodes, 3), dtype=np.float32),
            metadata={"order": ["x", "y", "z"]})

        new_resource.data_blocks["skin_index"] = DataBlock(
            data=np.empty((num_nodes, ), dtype=np.int16))

        new_resource.data_blocks["mesh_index"] = DataBlock(
            data=np.empty((num_nodes,), dtype=np.int16))

        for node_index, node in enumerate(nodes):
            num_children = len(node["children_indices"])
            new_resource.data_blocks["translation"].data[node_index, :] = node["translation"]
            new_resource.data_blocks["rotation"].data[node_index, :] = node["rotation"]
            new_resource.data_blocks["scale"].data[node_index, :] = node["scale"]
            new_resource.data_blocks["num_children"].data[node_index] = num_children
            new_resource.data_blocks["children_indices"].data[node_index, :num_children] = node["children_indices"]
            new_resource.data_blocks["parent_index"].data[node_index] = node["parent_index"]
            new_resource.data_blocks["mesh_index"].data[node_index] = node["mesh_index"]
            new_resource.data_blocks["skin_index"].data[node_index] = node["skin_index"]

        self.all_resources[f"{resource_uid}/nodes_0"] = new_resource

    def __load_animation_resources(self, resource_uid: str):

        for animation_index in range(self.gltf_reader.num_animations):

            new_resource = Resource(resource_type=constants.RESOURCE_TYPE_ANIMATION)
            animation = self.gltf_reader.get_animation(index=animation_index)

            # The data from gltf_reader needs to be re-organised in order to keep all animation data
            # pertaining to a node contiguous

            # Find all unique node indices and sort them
            translation_node_indices = [node_data["node_index"] for node_data in animation["translation"]]
            rotation_node_indices = [node_data["node_index"] for node_data in animation["rotation"]]
            scale_node_indices = [node_data["node_index"] for node_data in animation["scale"]]
            unique_node_indices = list(set(translation_node_indices + rotation_node_indices + scale_node_indices))
            unique_node_indices.sort()

            # Store node indices and timestamps
            new_resource.data_blocks["node_indices"] = DataBlock(data=np.array(unique_node_indices, dtype=np.int32))
            new_resource.data_blocks["timestamps"] = DataBlock(data=animation["timestamps"])

            # Store channel data into bit matrix
            num_node_tracks = len(unique_node_indices)
            num_timestamps = animation["timestamps"].size

            # Create empty data blocks first
            new_resource.data_blocks["translation"] = DataBlock(
                data=np.empty((num_timestamps, num_node_tracks, 3), dtype=np.float32),
                metadata={"order": ["x", "y", "z"]})

            new_resource.data_blocks["rotation"] = DataBlock(
                data=np.empty((num_timestamps, num_node_tracks, 4), dtype=np.float32),
                metadata={"order": ["x", "y", "z", "w"], "type": "quaternion"})

            new_resource.data_blocks["scale"] = DataBlock(
                data=np.empty((num_timestamps, num_node_tracks, 3), dtype=np.float32),
                metadata={"order": ["x", "y", "z"]})

            # And populate them with their respective animation data after
            for node_index in unique_node_indices:
                for channel_name in constants.RESOURCE_ANIMATION_GLTF_CHANNELS:
                    node_sub_index = np.where(new_resource.data_blocks["node_indices"].data == node_index)[0]

                    channel_data = [node["data"] for node in animation[channel_name]
                                    if node["node_index"] == node_index][0]

                    reshaped_channel_data = np.reshape(channel_data, (channel_data.shape[0], 1, channel_data.shape[1]))

                    new_resource.data_blocks[channel_name].data[:, node_sub_index, :] = reshaped_channel_data

            # Finally, add the new animation resource
            self.all_resources[f"{resource_uid}/animation_{animation_index}"] = new_resource
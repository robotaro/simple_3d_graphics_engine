import numpy as np

from src.core import constants
from src.core.resource_loaders.resource import Resource
from src.core.data_block import DataBlock
from src.core.resource_loaders.resource_loader import ResourceLoader

from src.utilities import utils_gltf_reader


class ResourceLoaderGLTF(ResourceLoader):

    def __init__(self, all_resources: dict):
        super().__init__(all_resources=all_resources)

    def load(self, resource_uid: str, fpath: str) -> bool:
        gltf_reader = utils_gltf_reader.GLTFReader()
        gltf_reader.load(gltf_fpath=fpath)

        # Meshes
        for mesh_index, mesh in enumerate(gltf_reader.get_all_meshes()):

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

        # Nodes
        nodes = gltf_reader.get_nodes()

        # Animation
        for animation_index in range(gltf_reader.num_animations):

            new_resource = Resource(resource_type=constants.RESOURCE_TYPE_ANIMATION)
            animation = gltf_reader.get_animation(index=animation_index)

            # The data from gltf_reader needs to be re-organised in order to keep all animation data
            # pertaining to a node contiguous

            # Step 1) Find all unique node indices and sort them
            translation_node_indices = [node_data["node_index"] for node_data in animation["translation"]]
            rotation_node_indices = [node_data["node_index"] for node_data in animation["rotation"]]
            scale_node_indices = [node_data["node_index"] for node_data in animation["scale"]]
            unique_node_indices = list(set(translation_node_indices + rotation_node_indices + scale_node_indices))
            unique_node_indices.sort()

            # Step 2) Store node indices and timestamps
            new_resource.data_blocks["node_indices"] = DataBlock(data=np.array(unique_node_indices, dtype=np.int32))
            new_resource.data_blocks["timestamps"] = DataBlock(data=animation["timestamps"])

            # Step 3) Store channel data into bit matrix
            num_nodes = len(unique_node_indices)
            num_timestamps = animation["timestamps"].size

            new_resource.data_blocks["translation"] = DataBlock(
                data=np.ndarray((num_nodes, num_timestamps, 3), dtype=np.float32),
                metadata={"order": ["x", "y", "z"]})
            new_resource.data_blocks["rotation"] = DataBlock(
                data=np.ndarray((num_nodes, num_timestamps, 4), dtype=np.float32),
                metadata={"order": ["x", "y", "z", "w"], "type": "quaternion"})
            new_resource.data_blocks["scale"] = DataBlock(
                data=np.ndarray((num_nodes, num_timestamps, 3), dtype=np.float32),
                metadata={"order": ["x", "y", "z"]})

            for node_index in unique_node_indices:
                for channel_name in constants.RESOURCE_ANIMATION_GLTF_CHANNELS:
                    selected_node_data = [node["data"] for node in animation[channel_name]
                                          if node["node_index"] == node_index][0]
                    new_resource.data_blocks[channel_name] = selected_node_data

            self.all_resources[f"{resource_uid}/animation_{animation_index}"] = new_resource

        return True

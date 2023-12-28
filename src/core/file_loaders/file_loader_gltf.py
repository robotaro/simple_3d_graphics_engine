import numpy as np

from src.core import constants
from src.core.data_block import DataBlock
from src.core.data_group import DataGroup
from src.core.file_loaders.file_loader import FileLoader
from src.utilities import utils_gltf_reader


class FileLoaderGLTF(FileLoader):

    """
    The GLTF loader will load the following resources
    - Nodes (All nodes)
    - Meshes (Contain skinning info for specific skeletons)
    - Skeletons
    - Animations
    - Materials
    - Textures

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.gltf_reader = None

    def load(self, resource_uid: str, fpath: str) -> bool:
        self.gltf_reader = utils_gltf_reader.GLTFReader()
        self.gltf_reader.load(gltf_fpath=fpath)

        self.__load_nodes_resources(resource_uid=resource_uid)
        self.__load_mesh_resources(resource_uid=resource_uid)
        self.__load_skeleton_resources(resource_uid=resource_uid)
        self.__load_animation_resources(resource_uid=resource_uid)
        self.__load_skinning_resources(resource_uid=resource_uid)

        return True

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

        new_resource = DataGroup(archetype=constants.RESOURCE_TYPE_NODES_GLTF,
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

        self.external_data_groups[f"{resource_uid}/nodes"] = new_resource

    def __load_mesh_resources(self, resource_uid: str):

        for mesh_index, mesh in enumerate(self.gltf_reader.get_all_meshes()):

            new_resource = DataGroup(archetype=constants.RESOURCE_TYPE_MESH)
            new_resource.metadata["render_mode"] = mesh["render_mode"]
            mesh_attrs = mesh["attributes"]

            if "indices" in mesh:
                new_resource.data_blocks["indices"] = DataBlock(data=mesh["indices"])

            if "POSITION" in mesh_attrs:
                new_resource.data_blocks["vertices"] = DataBlock(data=mesh_attrs["POSITION"])

            if "NORMAL" in mesh_attrs:
                new_resource.data_blocks["normals"] = DataBlock(data=mesh_attrs["NORMAL"])

            # TODO: Check if there are more then on set of joints and weights (JOINTS_1, 2, etc)
            if "JOINTS_0" in mesh_attrs:
                new_resource.data_blocks["joints"] = DataBlock(data=mesh_attrs["JOINTS_0"])
                new_resource.metadata["unique_joint_skin_indices"] = np.sort(np.unique(mesh_attrs["JOINTS_0"])).tolist()

            if "WEIGHTS_0" in mesh_attrs:
                new_resource.data_blocks["weights"] = DataBlock(data=mesh_attrs["WEIGHTS_0"])

            self.external_data_groups[f"{resource_uid}/mesh_{mesh_index}"] = new_resource

    def __load_skeleton_resources(self, resource_uid: str):

        skins = self.gltf_reader.get_skins()



        """g = 0

        for joint_set in skeleton_joint_sets:
            skeleton_resource = self.extract_skeleton_from_nodes(joint_indices=list(joint_set),
                                                                 new_skeleton_uid="orange")
        g = 0

        animation = self.gltf_reader.get_animation(index=0)

        translation_node_indices = [node_data["node_index"] for node_data in animation["translation"]]
        rotation_node_indices = [node_data["node_index"] for node_data in animation["rotation"]]
        scale_node_indices = [node_data["node_index"] for node_data in animation["scale"]]
        unique_node_indices = list(set(translation_node_indices + rotation_node_indices + scale_node_indices))
        unique_node_indices.sort()

        g = 0"""
        pass

    def __load_animation_resources(self, resource_uid: str):

        new_resource = DataGroup(archetype=constants.RESOURCE_TYPE_MESH)

        animations = self.gltf_reader.get_animations()
        for animation_index, (channel_name, nodes) in enumerate(animations.items()):
            for node in nodes:

                # Combine timestamps with values
                combined_data = np.hstack((node['timestamps'][:, np.newaxis], node['values']))

                # Create a new DataBlock for each channel of each node
                # Set metadata based on the type of channel
                if channel_name == "rotation":
                    metadata = {"order": ["timestamp", "x", "y", "z", "w"], "type": "quaternion"}
                elif channel_name == "translation":
                    metadata = {"order": ["timestamp", "x", "y", "z"], "type": "vector3"}
                elif channel_name == "scale":
                    metadata = {"order": ["timestamp", "x", "y", "z"], "type": "vector3"}
                else:
                    raise ValueError(f"Unknown animation channel type: {channel_name}")

                data_block_key = f"node_{node['node_index']}/{channel_name}"
                new_resource.data_blocks[data_block_key] = DataBlock(data=combined_data, metadata=metadata)

        resource_key = f"{resource_uid}/animation_{animation_index}"
        self.external_data_groups[resource_key] = new_resource

        g = 0

    def __load_skinning_resources(self, resource_uid: str):

        #for skin_index, skin in enumerate(self.gltf_reader.get_skins()):
        #    new_resource = DataGroup(archetype=constants.RESOURCE_TYPE_ANIMATION)
        #    self.external_data_groups[f"{resource_uid}/skin_{skin_index}"] = new_resource
        g = 0

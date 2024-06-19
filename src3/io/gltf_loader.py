import numpy as np

from src.core import constants
from src.core.data_block import DataBlock
from src.core.data_group import DataGroup
from src.utilities import utils_gltf_reader


class GLTFLoader:

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

        self.__load_nodes_and_skeleton_resources(resource_uid=resource_uid)
        self.__load_mesh_resources(resource_uid=resource_uid)
        self.__load_animation_resources(resource_uid=resource_uid)
        self.__load_skinning_resources(resource_uid=resource_uid)

        return True

    def __load_nodes_and_skeleton_resources(self, resource_uid: str):

        # ================================================================================
        #                                   Nodes
        # ================================================================================

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

        nodes_resource = DataGroup(archetype=constants.RESOURCE_TYPE_NODES_GLTF,
                                   metadata={"node_names": node_names})

        nodes_resource.data_blocks["parent_index"] = DataBlock(
            data=np.ones((num_nodes,), dtype=np.int16) * -1)

        nodes_resource.data_blocks["num_children"] = DataBlock(
            data=np.zeros((num_nodes,), dtype=np.int16))

        nodes_resource.data_blocks["children_indices"] = DataBlock(
            data=np.ones((num_nodes, max_num_children), dtype=np.int16) * -1)

        nodes_resource.data_blocks["translation"] = DataBlock(
            data=np.zeros((num_nodes, 3), dtype=np.float32),
            metadata={"order": ["x", "y", "z"]})

        nodes_resource.data_blocks["rotation"] = DataBlock(
            data=np.zeros((num_nodes, 4), dtype=np.float32),
            metadata={"order": ["x", "y", "z", "w"], "type": "quaternion"})
        nodes_resource.data_blocks["rotation"].data[:, 3] = 1

        nodes_resource.data_blocks["scale"] = DataBlock(
            data=np.ones((num_nodes, 3), dtype=np.float32),
            metadata={"order": ["x", "y", "z"]})

        nodes_resource.data_blocks["skin_index"] = DataBlock(
            data=np.ones((num_nodes, ), dtype=np.int16) * -1)

        nodes_resource.data_blocks["mesh_index"] = DataBlock(
            data=np.ones((num_nodes,), dtype=np.int16) * -1)

        for node_index, node in enumerate(nodes):
            num_children = len(node["children_indices"])
            nodes_resource.data_blocks["translation"].data[node_index, :] = node["translation"]
            nodes_resource.data_blocks["rotation"].data[node_index, :] = node["rotation"]
            nodes_resource.data_blocks["scale"].data[node_index, :] = node["scale"]
            nodes_resource.data_blocks["num_children"].data[node_index] = num_children
            nodes_resource.data_blocks["children_indices"].data[node_index, :num_children] = node["children_indices"]
            nodes_resource.data_blocks["parent_index"].data[node_index] = node["parent_index"]
            nodes_resource.data_blocks["mesh_index"].data[node_index] = node["mesh_index"]
            nodes_resource.data_blocks["skin_index"].data[node_index] = node["skin_index"]

        self.external_data_groups[f"{resource_uid}/nodes"] = nodes_resource

        # ================================================================================
        #                           Skeleton (If any)
        # ================================================================================

        """
        parent_index -> node indices
        
        """

        #skeletons = self.gltf_reader.get_skeletons()

        num_nodes = len(nodes)
        skins = self.gltf_reader.get_skins()
        for skin_index, skin in enumerate(skins):

            # Build inverse reference maps to convert node indices to skeleton indices
            selected_node_indices = np.array(skin["joints"])
            node2skeleton_lookup = np.zeros((num_nodes,), dtype=np.int32)
            for skeleton_index, node_index in enumerate(selected_node_indices):
                node2skeleton_lookup[node_index] = skeleton_index

            skeleton_resource = DataGroup(archetype=constants.RESOURCE_TYPE_SKELETON,
                                          metadata={"node_indices": selected_node_indices})

            skeleton_resource.data_blocks["nodes2skeleton_lookup"] = DataBlock(data=node2skeleton_lookup)

            skeleton_resource.data_blocks["parent_index"] = DataBlock(
                data=nodes_resource.data_blocks["parent_index"].data[selected_node_indices])

            # Convert parent indices from their original node indices to skeleton indices
            skeleton_resource.data_blocks["parent_index"].data = node2skeleton_lookup[skeleton_resource.data_blocks["parent_index"].data]

            skeleton_resource.data_blocks["num_children"] = DataBlock(
                data=nodes_resource.data_blocks["num_children"].data[selected_node_indices])

            skeleton_resource.data_blocks["children_indices"] = DataBlock(
                data=nodes_resource.data_blocks["children_indices"].data[selected_node_indices, :])

            # Convert children indices from their original node indices to skeleton indices
            skeleton_resource.data_blocks["children_indices"].data = node2skeleton_lookup[skeleton_resource.data_blocks["children_indices"].data]

            skeleton_resource.data_blocks["translation"] = DataBlock(
                data=nodes_resource.data_blocks["translation"].data[selected_node_indices, :],
                metadata={"order": ["x", "y", "z"]})

            skeleton_resource.data_blocks["rotation"] = DataBlock(
                data=nodes_resource.data_blocks["rotation"].data[selected_node_indices, :],
                metadata={"order": ["x", "y", "z", "w"], "type": "quaternion"})

            skeleton_resource.data_blocks["scale"] = DataBlock(
                data=nodes_resource.data_blocks["scale"].data[selected_node_indices, :],
                metadata={"order": ["x", "y", "z"]})

            self.external_data_groups[f"{resource_uid}/skeleton_{skin_index}"] = skeleton_resource

    def __load_mesh_resources(self, resource_uid: str):

        for mesh_index, mesh in enumerate(self.gltf_reader.get_meshes()):

            new_resource = DataGroup(archetype=constants.RESOURCE_TYPE_MESH)
            new_resource.metadata["render_mode"] = mesh["render_mode"]
            mesh_attrs = mesh["attributes"]

            if "indices" in mesh:
                new_resource.data_blocks["indices"] = DataBlock(data=mesh["indices"])

            if "POSITION" in mesh_attrs:
                new_resource.data_blocks["vertices"] = DataBlock(data=mesh_attrs["POSITION"])

            if "NORMAL" in mesh_attrs:
                new_resource.data_blocks["normals"] = DataBlock(data=mesh_attrs["NORMAL"])

            if "TEXCOORD_0" in mesh_attrs:
                new_resource.data_blocks["uvs"] = DataBlock(data=mesh_attrs["TEXCOORD_0"])

            # TODO: Check if there are more then on set of joints and weights (JOINTS_1, 2, etc)
            if "JOINTS_0" in mesh_attrs:
                new_resource.data_blocks["joints"] = DataBlock(data=mesh_attrs["JOINTS_0"])
                new_resource.metadata["unique_joint_skin_indices"] = np.sort(np.unique(mesh_attrs["JOINTS_0"])).tolist()

            if "WEIGHTS_0" in mesh_attrs:
                new_resource.data_blocks["weights"] = DataBlock(data=mesh_attrs["WEIGHTS_0"])

            self.external_data_groups[f"{resource_uid}/mesh_{mesh_index}"] = new_resource

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

    def __load_skinning_resources(self, resource_uid: str):

        #for skin_index, skin in enumerate(self.gltf_reader.get_skins()):
        #    new_resource = DataGroup(archetype=constants.RESOURCE_TYPE_ANIMATION)
        #    self.external_data_groups[f"{resource_uid}/skin_{skin_index}"] = new_resource
        g = 0

    def calculate_node_depths(self, nodes, parent_index=-1, current_depth=0):
        for node_index, node in enumerate(nodes):
            if node["parent_index"] == parent_index:
                node["metadata"] = {"depth": current_depth}
                self. calculate_node_depths(nodes, parent_index=node_index, current_depth=current_depth + 1)

    def print_node_hierarchy(self, nodes):
        # Generate node names
        node_names = [node.get("name", f"node_{i}") for i, node in enumerate(nodes)]

        def _print_hierarchy(current_index, depth):
            print(" " * depth * 2 + f"[{current_index}] {node_names[current_index]}")  # 4 spaces per depth level
            for child_index in nodes[current_index]["children_indices"]:
                _print_hierarchy(child_index, depth + 1)

        # Find root nodes and start the recursion
        for index, node in enumerate(nodes):
            if node["parent_index"] == -1:
                _print_hierarchy(index, 0)

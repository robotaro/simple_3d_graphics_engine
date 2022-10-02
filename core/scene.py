import numpy as np

from core.node import Node
import glm

NO_PARENT_KEY = -1

class Scene:

    """
    The scene class if responsible for everything that is rendered on the screen. From cameras to
    """

    def __init__(self, engine):

        self.engine = engine
        self.cameras = dict()
        self.nodes = dict()
        self.meshes = dict()
        self.textures = dict()
        self.root_node_key = None

    def update_nodes(self):
        self.__update_node(index=self.root_node_key)

    def __update_node(self,
                      index: int,
                      parent_index=NO_PARENT_KEY) -> None:

        node = self.nodes[index]

        if parent_index in self.nodes:
            node.world_matrix = self.nodes[parent_index].world_matrix * node.local_matrix
        else:
            node.world_matrix = node.local_matrix

        for child_index in node.child_indices:
            self.__update_node(index=child_index, parent_index=index)

    def create_node(self, name="", parent_index=-1) -> int:



        pass


    def from_gltf_blueprint(self, blueprint: dict, scene_index=0):

        """
        This
        :param scene_blueprint:
        :return:
        """

        scene = blueprint['scenes'][scene_index]

        self.root_node_key = scene['root_node_index']

        # NODES
        for index, node in blueprint['nodes'].items():
            new_node = Node(name=node['name'])
            new_node.child_indices = node['child_indices']
            new_node.mesh_index = node['mesh_index']
            if node['matrix'] is not None:
                new_node.local_matrix = glm.mat4.from_bytes(node['matrix'].tobytes())
            new_node.rotation = node['rotation']
            new_node.translation = node['translation']
            new_node.scale = node['scale']
            self.nodes[index] = new_node

        # Update all nodes starting from the root node
        self.__update_node(index=self.root_node_key)

        # MESHES


        g = 0





    def render(self):

        pass

from bs4 import BeautifulSoup
from core.scene.scene import Scene
from core.scene.node import Node
from core.scene.renderables.light import Light
from core.scene.renderables.chessboard import ChessboardPlane

from core.utilities import utils_xml


class SceneLoader:

    def __init__(self):

        pass

    def load(self, scene_xml_fpath: str) -> None:

        """
        Loads current UI described in the ui blueprint
        :param blueprint_xml_fpath:
        :param theme_json_fpath:
        :return: None
        """

        # Load UI window blueprint
        with open(scene_xml_fpath) as file:
            root_soup = BeautifulSoup(file.read(), features="lxml")

            # Find window root node - there should be only one
            scene_soup = root_soup.find("scene")
            if scene_soup is None:
                raise ValueError(f"[ERROR] Could not find Scene node")

            new_scene = Scene()

            self.build_node_tree(parent_soup=scene_soup, parent_node=new_scene)

        # DEBUG
        new_scene.print_hierarchy()

    def build_node_tree(self, parent_soup: BeautifulSoup, parent_node: Node, level=0):

        level += 1

        for child_soup in parent_soup.findChildren(recursive=False):
            new_node = None

            if child_soup.name == "light":
                new_node = self.soup2light(soup=child_soup)
                parent_node.add(new_node)

            if new_node is None:
                raise ValueError(f"[ERROR] Node type {child_soup.name} is not supported")

            self.build_node_tree(parent_soup=child_soup, parent_node=new_node, level=level)

    def soup2light(self, soup: BeautifulSoup) -> Light:

        position = utils_xml.get_attribute_tuple_float(soup=soup, attribute="position")
        if position is None:
            position = (0.0, 0.0, 0.0)

        color = utils_xml.get_attribute_tuple_float(soup=soup, attribute="color")
        if color is None:
            color = (1.0, 1.0, 1.0, 1.0)

        return Light(light_color=color, position=position)

    def soup2chessboard_plane(self, soup: BeautifulSoup) -> ChessboardPlane:

        position = utils_xml.get_attribute_tuple_float(soup=soup, attribute="position")
        if position is None:
            position = (0.0, 0.0, 0.0)

        color = utils_xml.get_attribute_tuple_float(soup=soup, attribute="color")
        if color is None:
            color = (1.0, 1.0, 1.0, 1.0)

        return ChessboardPlane(light_color=color, position=position)

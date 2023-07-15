from bs4 import BeautifulSoup
from core.scene.scene import Scene
from core.scene.node import Node
from core.scene.renderables.light import Light

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

    def build_node_tree(self, parent_soup: BeautifulSoup, parent_node: Node, level=0):

        level += 1

        for child_soup in parent_soup.findChildren(recursive=False):
            new_node = None

            if child_soup.name == "light":
                new_node = self.soup2light(soup=child_soup, level=level)
                parent_node.add(new_node)

            # DEBUG
            continue


            if new_node is None:
                raise ValueError(f"[ERROR] Widget type {child_soup.name} is not supported")

            self.build_node_tree(parent_soup=child_soup, parent_widget=new_widget, level=level)


    def soup2light(self, soup: BeautifulSoup, level: int) -> None:

        # Get String Parameters
        position = utils_xml.get_attribute_tuple_float(soup=soup, attribute="position")
        if position is None:
            position = (0.0, 0.0, 0.0)

        # Convert string paramters to
        return

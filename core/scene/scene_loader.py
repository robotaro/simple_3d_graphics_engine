from bs4 import BeautifulSoup
from core.scene.scene import Scene
from core.scene.node import Node


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

            #new_scene = Scene()

            self.build_node_tree(parent_soup=scene_soup, parent_node=new_scene)

    def build_node_tree(self, parent_soup: BeautifulSoup, parent_node: Node, level=0):

        level += 1

        for child_soup in parent_soup.findChildren(recursive=False):
            new_widget = None

            #if ui_constants.KEY_ATTRS_ID not in child_soup.attrs:
            #    raise AttributeError(f"[ERROR] Missing widget ID on {child_soup.attrs.name} widget")

            if child_soup.name == "light":
                new_node = self.soup2light(soup=child_soup, level=level)
                parent_widget.add_child_widget(widget=new_widget)

            if new_widget is None:
                raise ValueError(f"[ERROR] Widget type {child_soup.name} is not supported")

            self.build_node_tree(parent_soup=child_soup, parent_widget=new_widget, level=level)



    def soup2light(self, soup: BeautifulSoup, level: int) -> None:

        # Get String Parameters
        position = self._get_attrs_position(soup=soup)

        # Convert string paramters to
        pass

    def _get_attrs_position(self, soup: BeautifulSoup) -> tuple:
        position_str = soup.attrs.get("position", "0 0 0")
        return tuple([float(part) for part in position_str.strip(" ").split(" ")])

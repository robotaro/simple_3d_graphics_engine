import os
import xml.etree.ElementTree as ET

from src.utilities import utils_string


KEY_NAME = "name"
KEY_LINK = "link"
KEY_JOINT = "joint"
KEY_VISUAL = "visual"


def load_urdf(self, fpath: str, root_name="robot"):
    tree = None
    with open(fpath, "r") as xml_file:
        xml_string = xml_file.read()

        # Parse XML file
        tree = ET.fromstring(xml_string)
    if tree is None:
        raise FileNotFoundError(f"[ERROR] File not found {fpath}")

    # Find robot element
    root = None
    for child in tree:
        name = child.attrib.get(KEY_NAME, None)
        if name is None:
            raise ValueError("[ERROR] 'name' is missing")

        if child.tag == KEY_LINK:
            self.links[name] = self.parse_link(link=child)

        if child.tag == KEY_JOINT:
            self.joints[name] = self.parse_joint(joint=child)

    if root is None:
        raise Exception(f"[ERROR] Root element '{root_name}' not found")


def parse_link(self, link) -> dict:
    new_link = {}

    for component in link:
        if component.tag == KEY_VISUAL:
            new_link[KEY_VISUAL] = component

        if component.tag == "collision":
            new_link[KEY_VISUAL] = component

        if component.tag == "inertial":
            new_link[KEY_VISUAL] = component


def parse_joint(self, joint):
    g = 0
    pass
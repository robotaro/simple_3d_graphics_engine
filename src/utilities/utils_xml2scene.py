import os
import yaml
from typing import Tuple
import xml.etree.ElementTree as ET


def load_scene_from_xml(xml_fpath: str) -> Tuple[dict, dict]:
    """
    Loads scene from XML to serialised dictionary format. This format is the universal format for saving
    and loading scenes
    """

    if not os.path.isfile(xml_fpath):
        raise FileNotFoundError(f"[ERROR] File '{xml_fpath}' not found or cannot be opened.")

    xml_string = ""
    with open(xml_fpath, "r") as xml_file:
        xml_string = xml_file.read()

    root_element = ET.fromstring(xml_string)
    if root_element.tag != "scene":
        raise ValueError(f"[ERROR] Could not fine root element 'scene' in file {xml_fpath}")

    xml_dir = os.path.dirname(xml_fpath)

    scene_resources = {}
    if "resources" in root_element.attrib:
        resources_fpath = os.path.join(xml_dir, root_element.attrib["resources"])
        with open(resources_fpath, 'r') as file:
            scene_resources = yaml.safe_load(file)

    scene_blueprint = {root_element.tag: xml_element_to_dict(root_element)}

    return scene_blueprint, scene_resources


def xml_element_to_dict(element):

    if len(element) == 0:
        result = element.attrib.copy()
        if element.text:
            result["text"] = element.text.strip()
        return result

    result = {}
    components = []
    for child in element:

        child_data = xml_element_to_dict(child)

        # If this element is nto an entity, then it is its component
        if child.tag != "entity":
            component_name = child.tag
            component_params = {"name": component_name, "parameters": child_data}
            components.append(component_params)
            continue

        # If this tag has already been used, turn it into a list
        if child.tag in result:
            if isinstance(result[child.tag], list):
                result[child.tag].append(child_data)
            else:
                result[child.tag] = [result[child.tag], child_data]
        else:
            result[child.tag] = child_data

    attributes = element.attrib
    if attributes:
        result.update(attributes)

    if components:
        result["components"] = components

    return result

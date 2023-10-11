import os
import xml.etree.ElementTree as ET


def load_scene_from_xml(xml_fpath: str) -> dict:
    """
    Loads scene from XML to serialised dictionary format. This format is the universal format for saving
    and loading scenes
    """

    if not os.path.isfile(xml_fpath):
        raise FileNotFoundError(f"[ERROR] File '{xml_fpath}' not found or cannot be opened.")

    xml_string = ""
    with open(xml_fpath, "r") as xml_file:
        xml_string = xml_file.read()

    root = ET.fromstring(xml_string)
    if root.tag != "scene":
        raise ValueError(f"[ERROR] Could not fine root element 'scene' in file {xml_fpath}")

    scene_blueprint = {root.tag: xml_to_dict(root)}

    return scene_blueprint


def xml_to_dict(element):
    if len(element) == 0:
        result = element.attrib.copy()
        if element.text:
            result["text"] = element.text.strip()
        return result

    result = {}
    components = []
    for child in element:
        if child.tag != "entity":
            child_data = xml_to_dict(child)
            component_name = child.tag
            component_params = {"name": component_name, "parameters": child_data}
            components.append(component_params)
        else:
            child_data = xml_to_dict(child)
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

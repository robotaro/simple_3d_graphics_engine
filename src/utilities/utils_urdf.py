
import xml.etree.ElementTree as ET

from src.utilities import utils_string


KEY_NAME = "name"
KEY_LINK = "link"
KEY_JOINT = "joint"
KEY_VISUAL = "visual"
KEY_GEOMETRY = "geometry"
KEY_MESH = "mesh"
KEY_FILENAME = "filename"
KEY_BOX = "box"
KEY_SPHERE = "sphere"
KEY_MATERIAL = "material"
KEY_COLOR = "color"
KEY_AXIS = "axis"
KEY_LIMIT = "limit"
KEY_PARENT = "parent"
KEY_CHILD = "child"
KEY_ORIGIN = "origin"


def load_urdf(xml_fpath: str) -> dict:
    tree = None
    with open(xml_fpath, "r") as xml_file:
        xml_string = xml_file.read()
        tree = ET.fromstring(xml_string)

    if tree is None:
        raise FileNotFoundError(f"[ERROR] File not found {xml_fpath}")

    robot_blueprint = {"links": {}, "joints": {}}

    for child in tree:
        name = child.attrib.get(KEY_NAME, None)
        if name is None:
            raise ValueError("[ERROR] 'name' is missing")

        if child.tag == KEY_LINK:
            robot_blueprint["links"][name] = parse_link(link=child)

        if child.tag == KEY_JOINT:
            robot_blueprint["joints"][name] = parse_joint(joint=child)

    return robot_blueprint


def parse_link(link) -> dict:
    new_link = {}
    for child in link:
        if child.tag == KEY_VISUAL:
            new_link["visual"] = parse_visual(visual=child)

    return new_link


def parse_visual(visual) -> dict:

    visual_dict = {}
    for child in visual:
        if child.tag == KEY_GEOMETRY:
            visual_dict["geometry"] = parse_geometry(geometry=child)

        if child.tag == KEY_MATERIAL:
            visual_dict["material"] = parse_material(material=child)

    return visual_dict


def parse_geometry(geometry) -> dict:

    geometry_dict = {}
    for child in geometry:
        if child.tag == KEY_MESH:
            geometry_dict["mesh"] = {"fpath": child.attrib.get(KEY_FILENAME, "")}

        if child.tag == KEY_BOX:
            box_size = utils_string.string2tuple_float(input_value=child.attrib.get("size", None), default_value=(0.1, 0.1, 0.1))
            geometry_dict["box"] = {"size": box_size}

        if child.tag == KEY_SPHERE:
            radius = utils_string.string2float(input_value=child.attrib.get("radius", None), default_value=0.1)
            geometry_dict["sphere"] = {"radius": radius}

    return geometry_dict


def parse_material(material) -> dict:
    material_dict = {}
    for child in material:
        if child.tag == KEY_COLOR:
            rgba = utils_string.string2tuple_float(input_value=child.attrib.get("rgba", None), default_value=(0.85, 0.85, 0.85, 1.0))
            material_dict["color_rgba"] = rgba
    return material_dict


def parse_joint(joint) -> dict:

    joint_dict = {}
    for child in joint:
        if child.tag == KEY_AXIS:
            axis_xyz = utils_string.string2tuple_float(input_value=child.attrib["xyz"], default_value=(0.0, 0.0, 1.0))
            joint_dict["axis"] = {"xyz": axis_xyz}

        if child.tag == KEY_ORIGIN:
            position = utils_string.string2tuple_float(input_value=child.attrib.get("xyz", None),
                                                       default_value=(0.0, 0.0, 0.0))
            joint_dict["origin"] = {"xyz": position}
            rotation = utils_string.string2tuple_float(input_value=child.attrib.get("rpy", None),
                                                       default_value=(0.0, 0.0, 0.0))
            joint_dict["origin"] = {"rpy": rotation}

        if child.tag == KEY_LIMIT:
            effort = utils_string.string2float(input_value=child.attrib.get("effort", None),
                                               default_value=0.0)
            lower = utils_string.string2float(input_value=child.attrib.get("lower", None),
                                              default_value=0.0)
            upper = utils_string.string2float(input_value=child.attrib.get("upper", None),
                                              default_value=1.0)
            velocity = utils_string.string2float(input_value=child.attrib.get("velocity", None),
                                                 default_value=0.0)
            joint_dict["limit"] = {"effort": effort,
                                   "lower": lower,
                                   "upper": upper,
                                   "velocity": velocity}

        if child.tag == KEY_PARENT:
            joint_dict["parent"] = child.attrib.get(KEY_LINK, "")

        if child.tag == KEY_CHILD:
            joint_dict["child"] = child.attrib.get(KEY_LINK, "")

    return joint_dict

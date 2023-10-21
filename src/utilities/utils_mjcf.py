import xml.etree.ElementTree as ET

KEY_ASSET = "asset"
KEY_LINK = "link"
KEY_JOINT = "joint"
KEY_MATERIAL = "material"
KEY_MESH = "mesh"
KEY_WORLD = "worldbody"
KEY_BODY = "body"
KEY_BODY_NAME = "name"
KEY_GEOMETRY = "geom"
KEY_INERTIAL = "inertial"


def load_mjcf(xml_fpath: str) -> dict:

    tree = None
    with open(xml_fpath, "r") as xml_file:
        xml_string = xml_file.read()
        tree = ET.fromstring(xml_string)

    if tree is None:
        raise FileNotFoundError(f"[ERROR] File not found {xml_fpath}")

    robot_blueprint = {"assets": {}, "links": {}}

    for child in tree:

        if child.tag == KEY_ASSET:
            robot_blueprint["assets"] = parse_assets(assets=child)

        if child.tag == KEY_WORLD:
            robot_blueprint["links"] = parse_world(assets=child)

    return robot_blueprint


def parse_assets(assets: ET.Element) -> dict:

    materials = []
    meshes = []

    for child in assets:

        if child.tag == KEY_MATERIAL:
            materials.append(child.attrib)

        if child.tag == KEY_MESH:
            meshes.append(child.attrib)

    return {"materials": materials, "meshes": meshes}


def parse_world(assets: ET.Element) -> dict:

    bodies = {}

    for child in assets:

        if child.tag == KEY_BODY:
            parse_body_recursive(body=child, output_bodies=bodies)

        # TODO: add light nere

    return bodies


def parse_body_recursive(body: ET.Element, output_bodies: dict, parent_name=None):

    # Create a new body
    body_name = body.attrib[KEY_BODY_NAME]
    output_bodies[body_name] = body.attrib
    output_bodies[body_name]["parent"] = parent_name
    output_bodies[body_name]["geometry"] = []

    for child in body:

        if child.tag == KEY_BODY:
            parse_body_recursive(body=child, output_bodies=output_bodies, parent_name=body_name)

        if child.tag == KEY_JOINT:
            output_bodies[body_name]["joint"] = child.attrib

        if child.tag == KEY_GEOMETRY:
            output_bodies[body_name]["geometry"].append(child.attrib)

        if child.tag == KEY_INERTIAL:
            output_bodies[body_name]["inertial"] = child.attrib


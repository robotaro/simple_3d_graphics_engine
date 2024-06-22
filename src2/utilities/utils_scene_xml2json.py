from src.core import constants
import xml.etree.ElementTree as ET

SCENE_CONTAINER_NAME_CAMERAS = "cameras"
SCENE_CONTAINER_NAME_POINT_LIGHTS = "point_lights"
SCENE_CONTAINER_NAME_DIRECTIONAL_LIGHTS = "directional_lights"
SCENE_CONTAINER_NAME_ENTITIES = "entities"

OPTIONAL_KEY_LIST = ["id", "ref_id"]


def editor_xml2json(xml_fpath: str) -> dict:

    tree = ET.parse(xml_fpath)
    root = tree.getroot()  # root is "editor" element

    editor_blueprint = {
        constants.EDITOR_BLUEPRINT_KEY_RESOURCES: [],
        constants.EDITOR_BLUEPRINT_KEY_ENTITIES: [],
        constants.EDITOR_BLUEPRINT_KEY_COMPONENTS: [],
        constants.EDITOR_BLUEPRINT_KEY_SCENES: []
    }

    # Process elements inside root. tag = "editor"
    for child in root:

        # Scenes
        if child.tag in constants.EDITOR_BLUEPRINT_ENTITY_SCENE_TYPE:
            scene = parse_scene(scene_element=child)
            editor_blueprint[constants.EDITOR_BLUEPRINT_KEY_SCENES].append(scene)
            continue

        # Global Entities
        if child.tag in constants.EDITOR_BLUEPRINT_ENTITY_LIST_TYPE:
            entity = parse_entity(entity_element=child)
            editor_blueprint[constants.EDITOR_BLUEPRINT_KEY_ENTITIES].append(entity)
            continue

        # Global Components
        if child.tag in constants.EDITOR_BLUEPRINT_COMPONENT_LIST_TYPE:
            component = parse_component(component_element=child)
            editor_blueprint[constants.EDITOR_BLUEPRINT_KEY_COMPONENTS].append(component)
            continue

        # Resources
        if child.tag == "resource":
            resource_id = child.attrib.get(constants.BLUEPRINT_KEY_ID, None)
            if resource_id is None:
                raise ValueError("[ERROR] Resource defined in XML needs an 'id' field")
            resource_fpath = child.attrib.get("fpath", None)
            if resource_fpath is None:
                raise ValueError(f"[ERROR] Resource '{resource_id}' defined in XML needs an 'fpath' field")
            editor_blueprint[constants.EDITOR_BLUEPRINT_KEY_RESOURCES].append({"id": resource_id, "fpath": resource_fpath})
            continue

    # Flatten entity structure
    for entity in editor_blueprint[constants.EDITOR_BLUEPRINT_KEY_ENTITIES]:


        pass

    return editor_blueprint


def parse_scene(scene_element) -> dict:
    entities = []

    # Entities in a scene are expected to only use ref_id (for now)
    for entity in scene_element:
        entity_dict = parse_component(entity)
        entities.append(entity_dict)

    entity_dict = {
        "type": scene_element.tag,
        "params": {key: convert_value(value) for key, value in scene_element.attrib.items()
                   if key not in OPTIONAL_KEY_LIST},
        "entities": entities
    }

    for key in OPTIONAL_KEY_LIST:
        if key in scene_element.attrib:
            entity_dict[key] = scene_element.attrib[key]

    # Return the parsed entity as a dictionary with parameters and components
    return entity_dict


def parse_entity(entity_element) -> dict:

    components = {}

    # Process components and check for type duplicates
    for component in entity_element:

        component_dict = parse_component(component)

        if not "ref_id" in component_dict and not "id" in component_dict:
            component_dict["id"] = f"{entity_element.attrib['id']}/{component_dict['type']}"

        if component_dict["type"] in components:
            raise ValueError(f"[ERROR] Component type {component_dict['id']} is duplicated. "
                             f"Entities names must unique components")

        components[component_dict["type"]] = component_dict

    entity_dict = {
        "type": entity_element.tag,
        "params": {key: convert_value(value) for key, value in entity_element.attrib.items()
                   if key not in OPTIONAL_KEY_LIST},
        "components": components
    }

    for key in OPTIONAL_KEY_LIST:
        if key in entity_element.attrib:
            entity_dict[key] = entity_element.attrib[key]

    # Return the parsed entity as a dictionary with parameters and components
    return entity_dict


def parse_component(component_element) -> dict:
    """
    Create a dictionary with "id", "type" and "parameters"
    :param component_element:
    :param black_listed_keys:
    :return:
    """

    component_dict = {
        "type": component_element.tag,
        "params": {key: convert_value(value) for key, value in component_element.attrib.items()
                   if key not in OPTIONAL_KEY_LIST}
    }

    for key in OPTIONAL_KEY_LIST:
        if key in component_element.attrib:
            component_dict[key] = component_element.attrib[key]

    return component_dict


def convert_value(value):
    # Convert string values to appropriate types
    if value.isdigit():
        return int(value)
    try:
        return float(value)
    except ValueError:
        if value.lower() in ["true", "false"]:
            return value.lower() == "true"
        elif " " in value:  # possible list of numbers
            parts = value.split()
            return [convert_value(part) for part in parts]
        return value
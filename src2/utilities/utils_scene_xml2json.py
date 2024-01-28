from src.core import constants
import xml.etree.ElementTree as ET

SCENE_CONTAINER_NAME_CAMERAS = "cameras"
SCENE_CONTAINER_NAME_POINT_LIGHTS = "point_lights"
SCENE_CONTAINER_NAME_DIRECTIONAL_LIGHTS = "directional_lights"
SCENE_CONTAINER_NAME_ENTITIES = "entities"

COMPONENT_PARAMETER_BLACKLIST = ["name"]


def editor_xml2json(xml_fpath: str) -> dict:

    tree = ET.parse(xml_fpath)
    root = tree.getroot()  # root is "editor" element

    editor_data = {
        constants.EDITOR_BLUEPRINT_KEY_RESOURCES: {},
        constants.EDITOR_BLUEPRINT_KEY_ENTITIES: {},
        constants.EDITOR_BLUEPRINT_KEY_COMPONENTS: {}
    }

    # root tag: "editor"
    for child in root:

        # Entities
        if child.tag in constants.EDITOR_BLUEPRINT_ENTITY_LIST_TYPE:
            entity = parse_entity(entity_element=child)
            entity_id = child.attrib.get("id", None)
            if entity_id is None:
                raise ValueError("[ERROR] Entity defined in XML needs an 'id' field")
            editor_data[constants.EDITOR_BLUEPRINT_KEY_ENTITIES][entity_id] = entity
            continue

        if child.tag in constants.EDITOR_BLUEPRINT_COMPONENT_LIST_TYPE:
            component = parse_component(component_element=child)
            component_id = child.attrib.get("id", None)
            if component_id is None:
                raise ValueError("[ERROR] Component defined in XML needs an 'id' field")
            editor_data[constants.EDITOR_BLUEPRINT_KEY_COMPONENTS][component_id] = component
            continue

        # Resources
        if child.tag == "resource":
            resource_id = child.attrib.get("id", None)
            if resource_id is None:
                raise ValueError("[ERROR] Resource defined in XML needs an 'id' field")
            resource_fpath = child.attrib.get("fpath", None)
            if resource_fpath is None:
                raise ValueError(f"[ERROR] Resource '{resource_id}' defined in XML needs an 'fpath' field")
            editor_data[constants.EDITOR_BLUEPRINT_KEY_RESOURCES][resource_id] = resource_fpath
            continue

    return editor_data


def parse_scene(scene_element) -> tuple:
    scene_name = scene_element.attrib.get('name', None)
    if scene_name is None:
        raise ValueError("[ERROR] When parsing XML scene, you need to specify a name for the scene")

    scene = {
        "parameters": {},
        constants.SCENE_BLUEPRINT_KEY_SHARED_COMPONENTS: {},
        "entities": {}
    }

    for child_element in scene_element:

        if child_element.tag == constants.SCENE_BLUEPRINT_KEY_SHARED_COMPONENTS:
            scene[constants.SCENE_BLUEPRINT_KEY_SHARED_COMPONENTS] = parse_shared_components(
                shared_comp_element=child_element)
            continue

        entity_type = child_element.tag
        scene["entities"].setdefault(entity_type, [])
        scene["entities"][entity_type].append(parse_entity(entity_element=child_element))

    return scene_name, scene


def parse_entity(entity_element) -> dict:
    # Parse the parameters of the entity, excluding those in the blacklist
    parameters = {key: convert_value(value) for key, value in entity_element.attrib.items()
                  if key not in COMPONENT_PARAMETER_BLACKLIST}

    # Initialize a dictionary for components
    components = {}

    # Process components and check for type duplicates
    for component in entity_element:
        component_type = component.tag
        component_dict = parse_component(component)

        if component_type in components:
            raise ValueError(f"[ERROR] Component type '{component_type}' is duplicated. "
                             f"Entities names must unique components")

        # Append the parsed component to the corresponding list in components dict
        components.setdefault(component_type, {})
        components[component_type] = component_dict

    # Separate them into shared or unique
    unique_components = {}
    shared_components = {}
    for component_name, component in components.items():
        if "component_id" in component:
            shared_components[component_name] = component
            continue
        unique_components[component_name] = component

    # Return the parsed entity as a dictionary with parameters and components
    return {
        "id": entity_element.attrib.get("id", ""),
        "parameters": parameters,
        "unique_components": unique_components,
        "shared_components": shared_components}


def parse_shared_components(shared_comp_element) -> dict:
    shared_components = {}
    for shared_component in shared_comp_element:
        shared_comp_type = shared_component.tag
        component_name = shared_component.attrib.get('shared_ref', None)
        if component_name is None:
            raise ValueError("[ERROR] When parsing XML scene, shared components nee a 'shared_ref' field")
        shared_components.setdefault(shared_comp_type, {})
        shared_components[shared_comp_type][component_name] = parse_component(shared_component, ["shared_ref"])
    return shared_components


def parse_component(component_element, black_listed_keys=None) -> dict:
    black_listed_keys = [] if black_listed_keys is None else black_listed_keys
    return {key: convert_value(value) for key, value in component_element.attrib.items()
            if key not in black_listed_keys}


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
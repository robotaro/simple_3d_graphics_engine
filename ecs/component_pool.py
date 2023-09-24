import os
from bs4 import BeautifulSoup

from ecs import constants
from ecs.components.component import Component
from ecs.components.transform_3d import Transform3D
from ecs.components.mesh import Mesh
from ecs.components.material import Material
from ecs.components.renderable import Renderable
from ecs.components.camera import Camera
from ecs.components.input_control import InputControl
from ecs.components.text_2d import Text2D
from ecs.components.point_light import PointLight
from ecs.components.directional_light import DirectionalLight

from ecs.utilities import utils_string


class Entity:

    def __init__(self, name="", entity_type=-1):
        self.name = name
        self.sub_entities = []
        self.is_subcomponent = False


class ComponentPool:

    COMPONENT_CLASS_MAP = {
        constants.COMPONENT_TYPE_TRANSFORM_3D: Transform3D,
        constants.COMPONENT_TYPE_MESH: Mesh,
        constants.COMPONENT_TYPE_RENDERABLE: Renderable,
        constants.COMPONENT_TYPE_CAMERA: Camera,
        constants.COMPONENT_TYPE_MATERIAL: Material,
        constants.COMPONENT_TYPE_INPUT_CONTROL: InputControl,
        constants.COMPONENT_TYPE_TEXT_2D: Text2D,
        constants.COMPONENT_TYPE_POINT_LIGHT: PointLight,
        constants.COMPONENT_TYPE_DIRECTIONAL_LIGHT: DirectionalLight
    }

    def __init__(self):

        # TODO: We start from 2 to make it easy to discern the background [0, 1]
        self.entity_uid_counter = constants.COMPONENT_POOL_STARTING_ID_COUNTER

        # For holding states!
        self.entities = {}

        # Components
        self.transform_3d_components = {}
        self.transform_2d_components = {}
        self.camera_components = {}
        self.mesh_components = {}
        self.renderable_components = {}
        self.material_components = {}
        self.input_control_components = {}
        self.text_2d_components = {}
        self.directional_light_components = {}
        self.spot_light_components = {}
        self.point_light_components = {}

        self.component_storage_map = {
            constants.COMPONENT_TYPE_TRANSFORM_3D: self.transform_3d_components,
            constants.COMPONENT_TYPE_TRANSFORM_2D: self.transform_2d_components,
            constants.COMPONENT_TYPE_MESH: self.mesh_components,
            constants.COMPONENT_TYPE_RENDERABLE: self.renderable_components,
            constants.COMPONENT_TYPE_CAMERA: self.camera_components,
            constants.COMPONENT_TYPE_MATERIAL: self.material_components,
            constants.COMPONENT_TYPE_INPUT_CONTROL: self.input_control_components,
            constants.COMPONENT_TYPE_TEXT_2D: self.text_2d_components,
            constants.COMPONENT_TYPE_DIRECTIONAL_LIGHT: self.directional_light_components,
            constants.COMPONENT_TYPE_SPOT_LIGHT: self.spot_light_components,
            constants.COMPONENT_TYPE_POINT_LIGHT: self.point_light_components,
        }

        # This variable is a temporary solution to keep track of all entities added during the xml scene loading
        self.entity_uids_to_be_initiliased = []

    def create_entity(self, name="") -> int:
        uid = self.entity_uid_counter
        self.entities[uid] = Entity(name=name)
        self.entity_uid_counter += 1
        return uid

    def add_component(self, entity_uid: int, component_type: int, **kwargs):
        component_pool = self.component_storage_map.get(component_type, None)

        # Safety
        if component_pool is None:
            raise TypeError(f"[ERROR] Component type '{component_type}' not supported")
        if entity_uid in component_pool:
            raise TypeError(f"[ERROR] Component type '{component_type}' already exists in component pool")

        component_pool[entity_uid] = ComponentPool.COMPONENT_CLASS_MAP[component_type](**kwargs)
        return component_pool[entity_uid]

    def remove_component(self, entity_uid: int, component_type: str):

        if self.entities[entity_uid].is_subcomponent:
            raise Exception("[ERROR] Tried to remove sub-component directly")
        component_pool = self.component_storage_map.get(component_type, None)

        # Safety
        if component_pool is None:
            return

        component_pool[entity_uid].release()
        component_pool.pop(entity_uid)

    def get_component(self, entity_uid: int, component_type: str) -> Component:
        component_pool = self.component_storage_map.get(component_type, None)

        # Safety
        if component_pool is None:
            raise TypeError(f"[ERROR] Component type '{component_type}' not supported")

        return component_pool.get(entity_uid, None)

    def get_all_components(self, entity_uid: int) -> list:
        return [storage[entity_uid] for _, storage in self.component_storage_map.items() if entity_uid in storage]

    def get_entities_using_component(self, component_type: int) -> list:
        return list(self.component_storage_map[component_type].keys())

    # ================================================================================
    #                           Scene Loading Functions
    # ================================================================================

    def load_scene(self, scene_xml_fpath: str):

        # Check if path is absolute
        fpath = None
        if os.path.isfile(scene_xml_fpath):
            fpath = scene_xml_fpath

        if fpath is None:
            # Assume it is a relative path from the working directory/root directory
            clean_scene_xml_fpath = scene_xml_fpath.replace("\\", os.sep).replace("/", os.sep)
            fpath = os.path.join(constants.ROOT_DIR, clean_scene_xml_fpath)

        # Load UI window blueprint
        with open(fpath) as file:
            root_soup = BeautifulSoup(file.read(), features="lxml")

            # Find window root node - there should be only one
            ui_soup = root_soup.find("scene")
            if ui_soup is None:
                raise ValueError(f"[ERROR] Could not find root 'scene' element")

            for entity_soup in root_soup.find_all("entity"):

                entity_name = entity_soup.attrs.get("name", "unamed_entity")
                entity_uid = self.create_entity(name=entity_name)

                self.entity_uids_to_be_initiliased.append(entity_uid)
                self._add_entity_components(entity_uid=entity_uid, entity_soup=entity_soup)

    def _add_entity_components(self, entity_uid: int, entity_soup: BeautifulSoup) -> None:
        """
        This function uses the Beautifulsoup element provided to add all the components
        assigned to the entity UID.
        :param entity_uid: int,
        :param entity_soup:
        :return: None
        """

        for component_soup in entity_soup.find_all():

            # Transform 3D
            if component_soup.name == constants.COMPONENT_NAME_TRANSFORM_3D:
                position_str = component_soup.attrs.get("position", "0 0 0")
                position = utils_string.string2float_list(position_str)

                self.add_component(
                    entity_uid=entity_uid,
                    component_type=constants.COMPONENT_TYPE_TRANSFORM_3D,
                    position=position)
                continue

            # Transform 2D
            if component_soup.name == constants.COMPONENT_NAME_TRANSFORM_2D:
                continue

            # Mesh
            if component_soup.name == constants.COMPONENT_NAME_MESH:
                shape = component_soup.attrs.get("shape", None)
                if shape is None:
                    raise Exception("You need to specify the shape of the mesh you want to create.")

                # Shape: OBJ
                if shape == constants.MESH_SHAPE_FROM_OBJ:
                    fpath = component_soup.attrs.get("fpath", None)
                    if shape is None:
                        raise Exception("You need to specify the location of the .obj file")

                    self.add_component(
                        entity_uid=entity_uid,
                        component_type=constants.COMPONENT_TYPE_MESH,
                        shape=shape,
                        fpath=fpath)

                # Shape: BOX
                if shape == constants.MESH_SHAPE_BOX:
                    self.add_component(
                        entity_uid=entity_uid,
                        component_type=constants.COMPONENT_TYPE_MESH,
                        shape=shape,
                        width=float(component_soup.attrs.get("width", "1.0")),
                        height=float(component_soup.attrs.get("height", "1.0")),
                        depth=float(component_soup.attrs.get("depth", "1.0")))

                # Shape: ICOSPHERE
                if shape == constants.MESH_SHAPE_ICOSPHERE:
                    self.add_component(
                        entity_uid=entity_uid,
                        component_type=constants.COMPONENT_TYPE_MESH,
                        shape=shape,
                        radius=float(component_soup.attrs.get("radius", "0.2")),
                        subdivisions=int(component_soup.attrs.get("subdivisions", "3")))
                continue

            # Camera
            if component_soup.name == constants.COMPONENT_NAME_CAMERA:
                viewport_norm_str = component_soup.attrs.get("viewport_ratio", "0.0 0.0 1.0 1.0")
                perspective_str = component_soup.attrs.get("perspective", "true")

                viewport_norm = tuple(utils_string.string2int_list(viewport_norm_str))
                perspective = utils_string.str2bool(perspective_str)

                self.add_component(
                    entity_uid=entity_uid,
                    component_type=constants.COMPONENT_TYPE_CAMERA,
                    viewport_norm=viewport_norm,
                    perspective=perspective)
                continue

            # Renderable
            if component_soup.name == constants.COMPONENT_NAME_RENDERABLE:
                self.add_component(
                    entity_uid=entity_uid,
                    component_type=constants.COMPONENT_TYPE_RENDERABLE)
                continue

            # Material
            if component_soup.name == constants.COMPONENT_NAME_MATERIAL:

                diffuse_str = component_soup.attrs.get("diffuse", ".75 .75 .75")
                specular_str = component_soup.attrs.get("ambient", "1.0 1.0 1.0")

                diffuse = tuple(utils_string.string2float_list(diffuse_str))
                specular = tuple(utils_string.string2float_list(specular_str))

                shininess_factor = float(component_soup.attrs.get("shininess_factor", "32.0"))
                metallic_factor = float(component_soup.attrs.get("metallic_factor", "1.0"))
                roughness_factor = float(component_soup.attrs.get("roughness_factor", "0.0"))

                self.add_component(
                    entity_uid=entity_uid,
                    component_type=constants.COMPONENT_TYPE_MATERIAL,
                    diffuse=diffuse,
                    specular=specular,
                    shininess_factor=shininess_factor,
                    metallic_factor=metallic_factor,
                    roughness_factor=roughness_factor)

                continue

            # Input Control
            if component_soup.name == constants.COMPONENT_NAME_INPUT_CONTROL:
                self.add_component(
                    entity_uid=entity_uid,
                    component_type=constants.COMPONENT_TYPE_INPUT_CONTROL)
                continue

            # Text 2D
            if component_soup.name == constants.COMPONENT_NAME_TEXT_2D:
                font_name = component_soup.attrs.get("font_name", None)
                if font_name is None:
                    raise Exception("You need to specify the font")

                text_component = self.add_component(
                    entity_uid=entity_uid,
                    component_type=constants.COMPONENT_TYPE_TEXT_2D,
                    font_name=font_name)

                # Add text, if present
                text = entity_soup.text.strip()
                if len(text) > 0:
                    text_component.set_text(text=text)
                continue

            # Directional Light
            if component_soup.name == constants.COMPONENT_NAME_DIRECTIONAL_LIGHT:
                diffuse_str = component_soup.attrs.get("diffuse", "1.0 1.0 1.0")
                specular_str = component_soup.attrs.get("ambient", "1.0 1.0 1.0")

                diffuse = tuple(utils_string.string2float_list(diffuse_str))
                specular = tuple(utils_string.string2float_list(specular_str))

                self.add_component(
                    entity_uid=entity_uid,
                    component_type=constants.COMPONENT_TYPE_DIRECTIONAL_LIGHT,
                    diffuse=diffuse,
                    specular=specular)
                continue

            # Point Light
            if component_soup.name == constants.COMPONENT_NAME_POINT_LIGHT:
                position_str = component_soup.attrs.get("position", "22.0 16.0 50.0")
                color_str = component_soup.attrs.get("color", "1.0 1.0 1.0")

                position = utils_string.string2float_list(position_str)
                color = utils_string.string2float_list(color_str)

                self.add_component(
                    entity_uid=entity_uid,
                    component_type=constants.COMPONENT_TYPE_POINT_LIGHT,
                    position=position,
                    color=color)
                continue

            # If you got here, it means the component you selected is not supported :(
            entity_name = entity_soup.attrs.get("name", "")
            if len(entity_name) > 0:
                entity_name = f" ({entity_name})"
                self.logger.error(f"Component {component_soup.name}, declared in entity uid "
                                  f"{entity_uid}{entity_name}, is not supported.")



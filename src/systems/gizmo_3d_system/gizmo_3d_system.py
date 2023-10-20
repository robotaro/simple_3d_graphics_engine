import logging
import moderngl

from src import constants
from src.event_publisher import EventPublisher
from src.action_publisher import ActionPublisher
from src.component_pool import ComponentPool
from src.math import intersection_3d
from src.utilities import utils_camera
from src.systems.system import System
from src.systems.gizmo_3d_system.gizmo_blueprint import GIZMO_3D_RIG_BLUEPRINT


class Gizmo3DSystem(System):

    _type = "gizmo_3d_system"

    __slots__ = [
        "entity_ray_intersection_list",
        "window_size",
        "gizmo_3d_rig_entity_uid",
        "selected_entity_uid",
        "selected_entity_init_distance_to_cam"]

    def __init__(self, logger: logging.Logger,
                 component_pool: ComponentPool,
                 event_publisher: EventPublisher,
                 action_publisher: ActionPublisher,
                 parameters: dict,
                 **kwargs):

        super().__init__(logger=logger,
                         component_pool=component_pool,
                         event_publisher=event_publisher,
                         action_publisher=action_publisher,
                         parameters=parameters)

        self.window_size = None
        self.entity_ray_intersection_list = []
        self.gizmo_3d_rig_entity_uid = None

        # DEBUG
        self.selected_entity_uid = None
        self.selected_entity_init_distance_to_cam = None

    def initialise(self) -> bool:
        """
        Initialises the Gizmo3D system using the parameters given

        :return: bool, TRUE if all steps of initialisation succeeded
        """

        # Create Gizmo entity here
        self.gizmo_3d_rig_entity_uid = self.component_pool.add_entity(
            entity_blueprint=GIZMO_3D_RIG_BLUEPRINT,
            system_owned=True)

        # Find out which cylinder is what axis and store their UIDs
        for entity_uid, gizmo_3d in self.component_pool.gizmo_3d_components.items():
            children_uids = self.component_pool.get_children_uids(entity_uid=entity_uid)

            for child_uid in children_uids:

                entity_name = self.component_pool.get_entity(child_uid).name

                if entity_name == constants.GIZMO_3D_SYSTEM_X_AXIS_NAME:
                    gizmo_3d.x_axis_entity_uid = child_uid
                    continue

                if entity_name == constants.GIZMO_3D_SYSTEM_Y_AXIS_NAME:
                    gizmo_3d.y_axis_entity_uid = child_uid
                    continue

                if entity_name == constants.GIZMO_3D_SYSTEM_Z_AXIS_NAME:
                    gizmo_3d.z_axis_entity_uid = child_uid
                    continue

        return True

    def on_event(self, event_type: int, event_data: tuple):

        if event_type == constants.EVENT_WINDOW_FRAMEBUFFER_SIZE:
            self.window_size = event_data

        if event_type == constants.EVENT_ENTITY_SELECTED:
            self.selected_entity_uid = event_data[0]

        if event_type == constants.EVENT_ENTITY_DESELECTED:
            self.selected_entity_uid = None

        if event_type == constants.EVENT_MOUSE_MOVE and self.window_size is not None:

            for entity_camera_id, camera_component in self.component_pool.camera_components.items():

                # Check if mouse is inside viewports
                if not camera_component.is_inside_viewport(coord_pixels=event_data):
                    continue

                view_matrix = self.component_pool.transform_3d_components[entity_camera_id].world_matrix
                projection_matrix = camera_component.get_projection_matrix(
                    window_width=self.window_size[0],
                    window_height=self.window_size[1])

                viewport_coord_norm = camera_component.get_viewport_coordinates(screen_coord_pixels=event_data)
                if viewport_coord_norm is None:
                    continue

                ray_direction, ray_origin = utils_camera.screen_to_world_ray(
                    viewport_coord_norm=viewport_coord_norm,
                    view_matrix=view_matrix,
                    projection_matrix=projection_matrix)

                for entity_entity_id, collider_component in self.component_pool.collider_components.items():

                    collider_transform = self.component_pool.transform_3d_components[entity_entity_id]

                    collision = False
                    if collider_component.shape == "sphere":
                        collision = intersection_3d.intersect_boolean_ray_sphere(
                            ray_origin=ray_origin,
                            ray_direction=ray_direction,
                            sphere_origin=collider_transform.world_matrix[:3, 3].flatten(),
                            sphere_radius=collider_component.radius)

                    material = self.component_pool.material_components[entity_entity_id]

                    # TODO: Consider "state variables" inside each component, that CAN be changed by events
                    material.state_highlighted = collision

    def update(self, elapsed_time: float, context: moderngl.Context) -> bool:

        gizmo = self.component_pool.gizmo_3d_components[self.gizmo_3d_rig_entity_uid]

        if self.selected_entity_uid is None:
            self.component_pool.mesh_components[gizmo.x_axis_entity_uid].visible = False
            self.component_pool.mesh_components[gizmo.y_axis_entity_uid].visible = False
            self.component_pool.mesh_components[gizmo.z_axis_entity_uid].visible = False
            return True

        self.component_pool.mesh_components[gizmo.x_axis_entity_uid].visible = True
        self.component_pool.mesh_components[gizmo.y_axis_entity_uid].visible = True
        self.component_pool.mesh_components[gizmo.z_axis_entity_uid].visible = True

        selected_transform = self.component_pool.transform_3d_components[self.selected_entity_uid]
        gizmo_transform = self.component_pool.transform_3d_components[self.gizmo_3d_rig_entity_uid]

        gizmo_transform.position = selected_transform.position
        gizmo_transform.rotation = selected_transform.rotation
        gizmo_transform.dirty = True

        return True

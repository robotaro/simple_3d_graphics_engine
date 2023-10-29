import logging
import moderngl
import numpy as np

from src.core import constants
from src.core.event_publisher import EventPublisher
from src.core.action_publisher import ActionPublisher
from src.core.component_pool import ComponentPool
from src.math import intersection_3d
from src.utilities import utils_camera
from src.systems.system import System
from src.systems.gizmo_3d_system.gizmo_blueprint import GIZMO_3D_RIG_BLUEPRINT


class Gizmo3DSystem(System):

    _type = "gizmo_3d_system"

    __slots__ = [
        "entity_ray_intersection_list",
        "window_size",
        "selected_entity_uid",
        "selected_entity_init_distance_to_cam",
        "gizmo_selection_enabled",
        "camera2gizmo_map",
        "mouse_screen_position"]

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
        self.gizmo_selection_enabled = True
        self.camera2gizmo_map = {}
        self.mouse_screen_position = (-1, -1)

        # DEBUG
        self.selected_entity_uid = None
        self.selected_entity_init_distance_to_cam = None

    def initialise(self) -> bool:
        """
        Initialises the Gizmo3D system using the parameters given

        :return: bool, TRUE if all steps of initialisation succeeded
        """

        # Stage 1) For every camera, create a gizmo entity and associate their ids
        for camera_entity_id, camera_component in self.component_pool.camera_components.items():
            if camera_entity_id in self.camera2gizmo_map:
                continue

            self.camera2gizmo_map[camera_entity_id] = self.component_pool.add_entity(
                entity_blueprint=GIZMO_3D_RIG_BLUEPRINT,
                system_owned=True)

        # Stage 2) For every gizmo3D, find out which meshes correspond to their respective axes
        for gizmo_3d_entity_uid, gizmo_3d_component in self.component_pool.gizmo_3d_components.items():

            children_uids = self.component_pool.get_children_uids(entity_uid=gizmo_3d_entity_uid)

            for child_uid in children_uids:

                entity_name = self.component_pool.get_entity(child_uid).name

                if entity_name == constants.GIZMO_3D_SYSTEM_X_AXIS_NAME:
                    gizmo_3d_component.x_axis_entity_uid = child_uid
                    continue

                if entity_name == constants.GIZMO_3D_SYSTEM_Y_AXIS_NAME:
                    gizmo_3d_component.y_axis_entity_uid = child_uid
                    continue

                if entity_name == constants.GIZMO_3D_SYSTEM_Z_AXIS_NAME:
                    gizmo_3d_component.z_axis_entity_uid = child_uid
                    continue

        # Step 3) Hide all gizmos before we begin
        #self.set_all_gizmo_3d_visibility(visible=False)

        return True

    def on_event(self, event_type: int, event_data: tuple):

        if event_type == constants.EVENT_WINDOW_FRAMEBUFFER_SIZE:
            self.window_size = event_data

        if event_type == constants.EVENT_ENTITY_SELECTED:
            self.selected_entity_uid = event_data[0]
            self.set_all_gizmo_3d_visibility(visible=True)

        if event_type == constants.EVENT_ENTITY_DESELECTED:
            self.selected_entity_uid = None
            self.set_all_gizmo_3d_visibility(visible=False)

        if event_type == constants.EVENT_MOUSE_LEAVE_UI:
            self.gizmo_selection_enabled = True

        if event_type == constants.EVENT_MOUSE_ENTER_UI:
            # TODO: Deselect gizmo when you enter the UI? Maybe think about it
            self.gizmo_selection_enabled = False

        if event_type == constants.EVENT_MOUSE_MOVE:
            self.mouse_screen_position = event_data
            self.mouse_move_highlight_demo(event_data=event_data)

    def update(self, elapsed_time: float, context: moderngl.Context) -> bool:

        for camera_entity_id, camera_component in self.component_pool.camera_components.items():

            if self.selected_entity_uid is None:
                continue

            # Find which gizmo is attached to this camera
            gizmo_3d_entity_uid = self.camera2gizmo_map[camera_entity_id]

            # Get both gizmo's and selected entity's transforms
            camera_transform_component = self.component_pool.transform_3d_components[camera_entity_id]
            selected_transform_component = self.component_pool.transform_3d_components[self.selected_entity_uid]
            gizmo_transform_component = self.component_pool.transform_3d_components[gizmo_3d_entity_uid]
            scale = utils_camera.get_gizmo_scale(camera_transform=camera_transform_component.world_matrix,
                                                 object_position=np.array(selected_transform_component.position,
                                                                          dtype=np.float32))

            # Put gizmo where the selected entity's is
            gizmo_transform_component.position = selected_transform_component.position
            gizmo_transform_component.rotation = selected_transform_component.rotation
            gizmo_transform_component.scale = scale

            gizmo_transform_component.dirty = True

        return True

    def set_all_gizmo_3d_visibility(self, visible=True):

        for camera_entity_id, camera_component in self.component_pool.camera_components.items():

            gizmo_3d_entity_uid = self.camera2gizmo_map[camera_entity_id]
            gizmo_3d_component = self.component_pool.gizmo_3d_components[gizmo_3d_entity_uid]

            self.component_pool.mesh_components[gizmo_3d_component.x_axis_entity_uid].visible = visible
            self.component_pool.mesh_components[gizmo_3d_component.y_axis_entity_uid].visible = visible
            self.component_pool.mesh_components[gizmo_3d_component.z_axis_entity_uid].visible = visible

    def perform_ray_axis_collision(self, camera_entity_uid: int) -> tuple:

        camera_component = self.component_pool.camera_components[camera_entity_uid]
        transform_component = self.component_pool.transform_3d_components[camera_entity_uid]

        view_matrix = self.component_pool.transform_3d_components[camera_entity_uid].world_matrix
        projection_matrix = camera_component.get_projection_matrix()

        viewport_coord_norm = camera_component.get_viewport_coordinates(screen_coord_pixels=self.mouse_screen_position)
        if viewport_coord_norm is None:
            return None, None

        return utils_camera.screen_to_world_ray(
            viewport_coord_norm=viewport_coord_norm,
            view_matrix=view_matrix,
            projection_matrix=projection_matrix)

    def mouse_move_highlight_demo(self, event_data: tuple):
        if self.window_size is None:
            return

        if not self.gizmo_selection_enabled:
            return

        for entity_camera_id, camera_component in self.component_pool.camera_components.items():

            # Check if mouse is inside viewports
            if not camera_component.is_inside_viewport(coord_pixels=event_data):
                continue

            view_matrix = self.component_pool.transform_3d_components[entity_camera_id].world_matrix
            projection_matrix = camera_component.get_projection_matrix()

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


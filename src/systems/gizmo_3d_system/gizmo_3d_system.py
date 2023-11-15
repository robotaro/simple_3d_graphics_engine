import logging
import moderngl
import numpy as np

from src.core import constants
from src.core.event_publisher import EventPublisher
from src.core.action_publisher import ActionPublisher
from src.core.component_pool import ComponentPool
from src.math import ray_intersection, mat4
from src.utilities import utils_camera
from src.systems.system import System
from src.systems.gizmo_3d_system.gizmo_blueprint import GIZMO_3D_RIG_BLUEPRINT


class Gizmo3DSystem(System):

    name = "gizmo_3d_system"

    __slots__ = [
        "entity_ray_intersection_list",
        "selected_entity_uid",
        "selected_entity_init_distance_to_cam",
        "original_active_local_matrix",
        "camera2gizmo_map",
        "mouse_screen_position",
        "gizmo_transformed_axes",
        "hover_axis_index",
        "gizmo_state",
        "event_handlers",
        "state_handlers",
        "gizmo_selection_enabled",
        "focused_camera_uid",
        "focused_gizmo_axis_index",
        "focused_gizmo_plane_index"
    ]

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

        self.entity_ray_intersection_list = []
        self.camera2gizmo_map = {}
        self.mouse_screen_position = (-1, -1)  # in Pixels
        self.gizmo_transformed_axes = np.eye(3, dtype=np.float32)

        # In-Use variables
        self.original_active_local_matrix = None

        # State variables
        self.gizmo_selection_enabled = True
        self.focused_gizmo_axis_index = -1
        self.focused_gizmo_plane_index = -1
        self.focused_camera_uid = None
        self.gizmo_state = constants.GIZMO_3D_STATE_NOT_HOVERING
        self.selected_entity_uid = None
        self.selected_entity_init_distance_to_cam = None

        self.event_handlers = {
            constants.EVENT_ENTITY_SELECTED: self.handle_event_entity_selected,
            constants.EVENT_ENTITY_DESELECTED: self.handle_event_entity_deselected,
            constants.EVENT_MOUSE_LEAVE_UI: self.handle_event_mouse_leave_ui,
            constants.EVENT_MOUSE_ENTER_UI: self.handle_event_mouse_enter_ui,
            constants.EVENT_MOUSE_MOVE: self.handle_event_mouse_move,
            constants.EVENT_MOUSE_BUTTON_PRESS: self.handle_event_mouse_button_press,
            constants.EVENT_MOUSE_BUTTON_RELEASE: self.handle_event_mouse_button_release,
        }

        self.state_handlers = {
            constants.GIZMO_3D_STATE_NOT_HOVERING: self.handle_state_not_hovering,
            constants.GIZMO_3D_STATE_HOVERING_AXIS: self.handle_state_hovering_axis,
            constants.GIZMO_3D_STATE_HOVERING_PLANE: self.handle_state_hovering_plane,
            constants.GIZMO_3D_STATE_TRANSLATING_ON_AXIS: self.handle_state_translate_on_axis,
            constants.GIZMO_3D_STATE_TRANSLATING_ON_PLANE: self.handle_state_translate_on_plane,
            constants.GIZMO_3D_STATE_ROTATE_AROUND_AXIS: self.handle_state_rotate_axis,
        }

    def initialise(self) -> bool:
        """
        Initialises the Gizmo3D system using the parameters given

        :return: bool, TRUE if all steps of initialisation succeeded
        """

        # Stage 1) For every camera, create a gizmo entity and associate their ids
        pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_CAMERA)
        for camera_entity_id, camera_component in pool.items():
            if camera_entity_id in self.camera2gizmo_map:
                continue

            # Create new gizmo entity for this camera
            gizmo_entity_uid = self.component_pool.add_entity(entity_blueprint=GIZMO_3D_RIG_BLUEPRINT,
                                                              system_owned=True)
            self.camera2gizmo_map[camera_entity_id] = gizmo_entity_uid

            # And make sure only this camera can render it
            gizmo_meshes = self.component_pool.get_all_sub_entity_components(
                parent_entity_uid=gizmo_entity_uid,
                component_type=constants.COMPONENT_TYPE_MESH)
            for mesh in gizmo_meshes:
                mesh.exclusive_to_camera_uid = camera_entity_id

        # Stage 2) For every gizmo3D, find out which meshes correspond to their respective axes
        pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_GIZMO_3D)
        for gizmo_3d_entity_uid, gizmo_3d_component in pool.items():

            children_uids = self.component_pool.get_children_uids(entity_uid=gizmo_3d_entity_uid)

            for index, axis_name in enumerate(constants.GIZMO_3D_AXES_NAME_ORDER):

                for child_uid in children_uids:

                    entity_name = self.component_pool.get_entity(child_uid).name

                    if entity_name == axis_name:
                        gizmo_3d_component.axes_entities_uids[index] = child_uid
                        continue

        # Step 3) Hide all gizmos before we begin
        self.set_all_gizmo_3d_visibility(visible=False)

        return True

    def on_event(self, event_type: int, event_data: tuple):
        handler = self.event_handlers.get(event_type, None)
        if handler is not None:
            handler(event_data=event_data)

    # ========================================================================
    #                             Event Handling
    # ========================================================================

    def handle_event_entity_selected(self, event_data: tuple):
        self.selected_entity_uid = event_data[0]
        self.set_all_gizmo_3d_visibility(visible=True)
        self.set_gizmo_to_selected_entity()

    def handle_event_entity_deselected(self, event_data: tuple):
        self.selected_entity_uid = None
        self.set_all_gizmo_3d_visibility(visible=False)

    def handle_event_mouse_enter_ui(self, event_data: tuple):
        self.gizmo_selection_enabled = False

    def handle_event_mouse_leave_ui(self, event_data: tuple):
        self.gizmo_selection_enabled = True

    def handle_event_mouse_move(self, event_data: tuple):
        print(f"move = {event_data}")
        self.mouse_screen_position = event_data

        if self.selected_entity_uid is None:
            return

        ray_origin, ray_direction, self.focused_camera_uid = self.screen2ray(screen_gl_pixels=event_data)
        if self.focused_camera_uid is None:
            return

        if ray_origin is None or ray_direction is None:
            return

        self.state_handlers[self.gizmo_state](ray_origin=ray_origin, ray_direction=ray_direction, mouse_press=False)

    def handle_event_mouse_button_press(self, event_data: tuple):
        if event_data[constants.EVENT_INDEX_MOUSE_BUTTON_BUTTON] != constants.MOUSE_LEFT:
            return

        if self.selected_entity_uid is None:
            return

        print(f"click = {event_data}")

        ray_origin, ray_direction, self.focused_camera_uid = self.screen2ray(screen_gl_pixels=event_data)
        if self.focused_camera_uid is None:
            return

        if ray_origin is None or ray_direction is None:
            print("None!")
            return

        self.state_handlers[self.gizmo_state](ray_origin=ray_origin, ray_direction=ray_direction, mouse_press=True)

    def handle_event_mouse_button_release(self, event_data: tuple):
        # When the LEFT MOUSE BUTTON is released, it should apply any transforms to the selected entity
        if event_data[constants.EVENT_INDEX_MOUSE_BUTTON_BUTTON] != constants.MOUSE_LEFT:
            return

        # TODO: Which state to move to? For not, I put not hovering, but this will create a bug
        self.gizmo_state = constants.GIZMO_3D_STATE_NOT_HOVERING
        self.event_publisher.publish(event_type=constants.EVENT_MOUSE_GIZMO_3D_DEACTIVATED,
                                     event_data=(None,),
                                     sender=self)

    # ========================================================================
    #                             State Handling
    # ========================================================================

    def handle_state_not_hovering(self, ray_origin: np.array, ray_direction: np.array, mouse_press: bool):
        print("not hovering")

        # AXIS COLLISION
        self.focused_gizmo_axis_index = self.mouse_ray_check_axes_collision(ray_origin=ray_origin,
                                                                            ray_direction=ray_direction)
        if self.focused_gizmo_axis_index == -1:
            return

        # PLANE COLLISION
        # TODO: Add collision check with planes
        self.gizmo_state = constants.GIZMO_3D_STATE_HOVERING_AXIS
        self.event_publisher.publish(event_type=constants.EVENT_MOUSE_ENTER_GIZMO_3D,
                                     event_data=(self.focused_gizmo_axis_index,), sender=self)

    def handle_state_hovering_axis(self, ray_origin: np.array, ray_direction: np.array, mouse_press: bool):
        print(f"hovering axis  - {self.focused_gizmo_axis_index}")
        if not self.gizmo_selection_enabled:
            return

        if mouse_press:
            self.gizmo_state = constants.GIZMO_3D_STATE_TRANSLATING_ON_AXIS
            transform = self.component_pool.get_component(entity_uid=self.selected_entity_uid,
                                                          component_type=constants.COMPONENT_TYPE_TRANSFORM_3D)
            self.original_active_local_matrix = transform.local_matrix.copy()
            self.event_publisher.publish(event_type=constants.EVENT_MOUSE_GIZMO_3D_ACTIVATED,
                                         event_data=(self.focused_gizmo_axis_index,),
                                         sender=self)
            return

        # Check if any other axis is now being hovered
        self.focused_gizmo_axis_index = self.mouse_ray_check_axes_collision(ray_origin=ray_origin,
                                                                            ray_direction=ray_direction)
        if self.focused_gizmo_axis_index == -1:
            self.gizmo_state = constants.GIZMO_3D_STATE_NOT_HOVERING
            return

        # PLANE COLLISION
        # TODO: Add collision check with planes

    def handle_state_hovering_plane(self, ray_origin: np.array, ray_direction: np.array, mouse_press: bool):
        pass

    def handle_state_translate_on_axis(self, ray_origin: np.array, ray_direction: np.array, mouse_press: bool):
        print("translating on Axis")
        pass

    def handle_state_translate_on_plane(self, screen_gl_pixels: tuple, entering_state: bool):
        """
        Handles mouse interaction when translating along an Axis. If this is the first time entering the
        state, use variable "entering_state" to allow the state to be initialised properly. This will happen
        when the mouse is first pressed
        :param screen_gl_pixels: current mouse location on screen
        :param entering_state: bool, should be TRUE if called from the MOUSE PRESS event callback
        :return:
        """
        pass

    def handle_state_rotate_axis(self, screen_gl_pixels: tuple, entering_state: bool):
        """
        Handles mouse interaction when translating along an Axis. If this is the first time entering the
        state, use variable "entering_state" to allow the state to be initialised properly. This will happen
        when the mouse is first pressed
        :param screen_gl_pixels: current mouse location on screen
        :param entering_state: bool, should be TRUE if called from the MOUSE PRESS event callback
        :return:
        """
        pass

    # ========================================================================
    #                            Core functions
    # ========================================================================

    def update(self, elapsed_time: float, context: moderngl.Context) -> bool:

        if self.selected_entity_uid is None:
            return True

        # Get component pools for easy access
        transform_3d_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_TRANSFORM_3D)

        selected_transform_component = transform_3d_pool[self.selected_entity_uid]
        selected_world_position = np.ascontiguousarray(selected_transform_component.world_matrix[:3, 3])

        camera_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_CAMERA)
        for camera_entity_uid, camera_component in camera_pool.items():

            # TODO: This also needs to be executed when you SELECT THE ENTITY!
            gizmo_3d_entity_uid = self.camera2gizmo_map[camera_entity_uid]
            gizmo_transform_component = transform_3d_pool[gizmo_3d_entity_uid]
            camera_matrix = transform_3d_pool[camera_entity_uid].world_matrix
            view_matrix = np.eye(4, dtype=np.float32)
            mat4.fast_inverse(in_mat4=camera_matrix, out_mat4=view_matrix)
            gizmo_scale = utils_camera.set_gizmo_scale(view_matrix=view_matrix, object_position=selected_world_position)
            viewport_height = camera_component.viewport_pixels[3]
            gizmo_scale *= constants.GIZMO_3D_VIEWPORT_SCALE_COEFFICIENT / viewport_height

            # Update gizmo's transform parameters for visual feedback
            gizmo_transform_component.position = selected_transform_component.position
            gizmo_transform_component.rotation = selected_transform_component.rotation
            gizmo_transform_component.scale = gizmo_scale
            gizmo_transform_component.input_values_updated = True

            self.dehighlight_gizmo(camera_uid=camera_entity_uid)
            self.highlight_active_gizmo_part(camera_uid=camera_entity_uid)

        return True

    # ========================================================================
    #                            Auxiliary functions
    # ========================================================================

    """def process_mouse_movement(self, screen_gl_pixels: tuple):

        if self.selected_entity_uid is None:
            return

        # Get mouse ray
        ray_origin, ray_direction = self.screen2ray(screen_gl_pixels=screen_gl_pixels)

        # Determine if mouse ray is intersection any structures
        self.update_state(ray_origin=ray_origin, ray_direction=ray_direction, mouse_press=False)

        self.dehighlight_gizmo()"""

    def screen2ray(self, screen_gl_pixels: tuple) -> tuple:
        """
        Converts any position in pixels using the OpenGL coordinates (not the viewport ones!) into a 3D ray with
        origin equal to the position of the camera and direction equal to its respective point on screen.

        All active viewports are tested to see which has the mouse and the ray is generated from it.

        :param screen_gl_pixels: tuple, pixel coordinates where zero os at the lower left corner of the screen
        :return: tuple, (ray_origin, ray_direction) <np.array, np.array>
        """

        active_camera_uid, active_camera_component = self.get_active_camera(screen_gl_pixels=screen_gl_pixels)
        if active_camera_uid is None:
            return None, None, None

        ray_origin, ray_direction = self.get_mouse_ray_point_on_axis(active_camera_uid=active_camera_uid,
                                                                     active_camera_component=active_camera_component)

        return ray_origin, ray_direction, active_camera_uid

    def process_gizmo_in_use(self, ray_origin: np.array, ray_direction: np.array) -> bool:
        if not self.gizmo_in_use:
            return False

        # TODO: CONTINUE FROM HERE !!!!!!!
        axis_origin = np.ascontiguousarray(self.original_active_local_matrix[:3, 3])
        axis_direction = np.ascontiguousarray(self.original_active_local_matrix[:3, self.gizmo_axis_on_hover_index])
        closest_points = ray_intersection.ray2ray_nearest_point(ray_0_origin=axis_origin,
                                                                ray_0_direction=axis_direction,
                                                                ray_1_origin=ray_origin,
                                                                ray_1_direction=ray_direction)
        # new_position = axis_origin + closest_points[0] *
        return True

    def get_active_camera(self, screen_gl_pixels: tuple) -> tuple:
        camera_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_CAMERA)
        active_camera_component = None
        active_camera_uid = None
        for camera_entity_id, camera_component in camera_pool.items():
            if not camera_component.is_inside_viewport(screen_gl_position=screen_gl_pixels):
                continue
            active_camera_component = camera_component
            active_camera_uid = camera_entity_id

        if active_camera_component is None:
            return None, None

        return active_camera_uid, active_camera_component

    def get_mouse_ray_point_on_axis(self, active_camera_uid: int, active_camera_component) -> tuple:

        """
        WHen a gizmo axis is being hovered by the mouse, this function returns where the closes point between that axis
        and the mouse's ray is.

        :param active_camera_uid: int
        :param active_camera_component: Camera
        :return: tuple
        """

        transform_3d_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_TRANSFORM_3D)

        gizmo_3d_entity_uid = self.camera2gizmo_map[active_camera_uid]

        gizmo_transform_component = transform_3d_pool[gizmo_3d_entity_uid]
        mat4.mul_vectors3(in_mat4=gizmo_transform_component.world_matrix,
                          in_vec3_array=constants.GIZMO_3D_AXES,
                          out_vec3_array=self.gizmo_transformed_axes)

        camera_matrix = transform_3d_pool[active_camera_uid].world_matrix
        projection_matrix = active_camera_component.get_projection_matrix()

        viewport_position = utils_camera.screen_gl_position_pixels2viewport_position(
            position_pixels=self.mouse_screen_position,
            viewport_pixels=active_camera_component.viewport_pixels)

        if viewport_position is None:
            return None, None

        ray_direction, ray_origin = utils_camera.screen_pos2world_ray(
            viewport_coord_norm=viewport_position,
            camera_matrix=camera_matrix,
            projection_matrix=projection_matrix)

        return ray_origin, ray_direction

    def mouse_ray_check_axes_collision(self, ray_origin: np.array, ray_direction: np.array) -> int:

        transform_3d_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_TRANSFORM_3D)
        gizmo_3d_entity_uid = self.camera2gizmo_map[self.focused_camera_uid] # TODO [CLEANUP] All I need is the gizmo transform
        gizmo_transform_component = transform_3d_pool[gizmo_3d_entity_uid]

        # TODO: [CLEANUP] Clean this silly code. Change the intersection function to accommodate for this
        points_a = np.array([gizmo_transform_component.position,
                             gizmo_transform_component.position,
                             gizmo_transform_component.position], dtype=np.float32)

        # Perform intersection test
        intersection_distances = np.empty((3,), dtype=np.float32)
        ray_intersection.intersect_ray_capsules(
            ray_origin=ray_origin,
            ray_direction=ray_direction,
            points_a=points_a,
            points_b=self.gizmo_transformed_axes,
            radius=np.float32(0.1 * gizmo_transform_component.scale),
            output_distances=intersection_distances)

        # Retrieve sub-indices of any axes being intersected by the mouse ray
        valid_axis_indices = np.where(intersection_distances > -1.0)[0]
        if valid_axis_indices.size == 0:
            return -1

        # And finally select the closest one to the camera
        return valid_axis_indices[intersection_distances[valid_axis_indices].argmin()]

    def mouse_ray_check_planes_collision(self, active_camera_uid: int, ray_origin: np.array, ray_direction: np.array):
        pass

    def dehighlight_gizmo(self, camera_uid: int):

        gizmo_3d_entity_uid = self.camera2gizmo_map[camera_uid]

        # De-highlight all axes
        material_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_MATERIAL)
        gizmo_3d_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_GIZMO_3D)
        gizmo_component = gizmo_3d_pool[gizmo_3d_entity_uid]
        for axis_entity_uid in gizmo_component.axes_entities_uids:
            material_pool[axis_entity_uid].state_highlighted = False

    def highlight_active_gizmo_part(self, camera_uid: int):

        if self.gizmo_state == constants.GIZMO_3D_STATE_NOT_HOVERING:
            return

        material_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_MATERIAL)
        gizmo_3d_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_GIZMO_3D)
        gizmo_component = gizmo_3d_pool[self.camera2gizmo_map[camera_uid]]
        axis_entity_uid = gizmo_component.axes_entities_uids[self.focused_gizmo_axis_index]
        axis_material = material_pool[axis_entity_uid]
        axis_material.state_highlighted = True

    def set_gizmo_to_selected_entity(self):

        transform_3d_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_TRANSFORM_3D)
        selected_transform_component = transform_3d_pool[self.selected_entity_uid]

        camera_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_CAMERA)
        for camera_entity_id, camera_component in camera_pool.items():

            gizmo_3d_entity_uid = self.camera2gizmo_map[camera_entity_id]
            gizmo_transform_component = transform_3d_pool[gizmo_3d_entity_uid]
            gizmo_transform_component.position = selected_transform_component.position
            gizmo_transform_component.rotation = selected_transform_component.rotation
            gizmo_transform_component.input_values_updated = True

    def set_all_gizmo_3d_visibility(self, visible=True):

        camera_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_CAMERA)
        gizmo_3d_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_GIZMO_3D)
        mesh_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_MESH)

        for camera_entity_id, camera_component in camera_pool.items():

            gizmo_3d_entity_uid = self.camera2gizmo_map[camera_entity_id]
            gizmo_3d_component = gizmo_3d_pool[gizmo_3d_entity_uid]

            for mesh_entity_uid in gizmo_3d_component.axes_entities_uids:
                mesh_pool[mesh_entity_uid].visible = visible

    def perform_ray_axis_collision(self, camera_entity_uid: int) -> tuple:

        camera_component = self.component_pool.camera_components[camera_entity_uid]
        transform_component = self.component_pool.transform_3d_components[camera_entity_uid]

        view_matrix = self.component_pool.transform_3d_components[camera_entity_uid].world_matrix
        projection_matrix = camera_component.get_projection_matrix()

        viewport_coord_norm = camera_component.get_viewport_coordinates(screen_coord_pixels=self.mouse_screen_position)
        if viewport_coord_norm is None:
            return None, None

        return utils_camera.screen_pos2world_ray(
            viewport_coord_norm=viewport_coord_norm,
            camera_matrix=view_matrix,
            projection_matrix=projection_matrix)



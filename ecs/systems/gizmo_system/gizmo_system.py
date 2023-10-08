import logging
import moderngl

from ecs import constants
from ecs.event_publisher import EventPublisher
from ecs.action_publisher import ActionPublisher
from ecs.systems.system import System
from ecs.component_pool import ComponentPool
from ecs.math import intersection_3d
from ecs.utilities import utils_camera


class GizmoSystem(System):

    _type = "gizmo_system"

    __slots__ = [
        "entity_ray_intersection_list",
        "window_size",
        "selected_entity_uid",
        "selected_entity_init_distance_to_cam"
    ]

    def __init__(self, logger: logging.Logger,
                 component_pool: ComponentPool,
                 event_publisher: EventPublisher,
                 action_publisher: ActionPublisher):
        super().__init__(logger=logger,
                         component_pool=component_pool,
                         event_publisher=event_publisher,
                         action_publisher=action_publisher)

        self.window_size = None
        self.entity_ray_intersection_list = []

        # DEBUG
        self.selected_entity_uid = None
        self.selected_entity_init_distance_to_cam = None

    def initialise(self, **kwargs) -> bool:
        return True

    def on_event(self, event_type: int, event_data: tuple):

        if event_type == constants.EVENT_WINDOW_FRAMEBUFFER_SIZE:
            self.window_size = event_data

        if event_type == constants.EVENT_ENTITY_SELECTED:
            self.selected_entity_uid = event_data[0]

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
                    material.is_highlighted = collision

    def update(self, elapsed_time: float, context: moderngl.Context) -> bool:

        for entity_uid, transform in self.component_pool.transform_3d_components.items():

            pass

        return True
import logging
import os.path

import moderngl

from src import constants
from src.event_publisher import EventPublisher
from src.action_publisher import ActionPublisher
from src.component_pool import ComponentPool
from src.math import intersection_3d
from src.utilities import utils_camera
from src.systems.system import System
from src.systems.gizmo_3d_system.gizmo_blueprint import GIZMO_BLUEPRINT


class ImportSystem(System):

    _type = "import_system"

    __slots__ = [
        "entity_ray_intersection_list",
        "window_size",
        "gizmo_entity_uid",
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
        self.gizmo_entity_uid = None

        # DEBUG
        self.selected_entity_uid = None
        self.selected_entity_init_distance_to_cam = None

    def initialise(self) -> bool:

        return True

    def on_event(self, event_type: int, event_data: tuple):

        if event_type == constants.EVENT_WINDOW_DROP_FILES:
            # Naive approach to check file type
            for fpath in event_data:
                directory, filename = os.path.split(fpath)
                filename_no_ext, extension = os.path.splitext(filename)
                # TODO: Continue from here!!!
                self.logger.debug(f"File dropped: {fpath}")

    def load_obj(self, fpath: str):
        pass

    def update(self, elapsed_time: float, context: moderngl.Context) -> bool:

        return True
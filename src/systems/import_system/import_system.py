import logging
import threading
import os.path

import moderngl

from src import constants
from src.systems.system import System
from src.event_publisher import EventPublisher
from src.action_publisher import ActionPublisher
from src.component_pool import ComponentPool

from src.systems.import_system.loading_task_obj import LoadingTaskObj


class ImportSystem(System):

    _type = "import_system"

    LOADING_TASK_CLASS = {
        "obj": LoadingTaskObj
    }

    __slots__ = [
        "entity_ray_intersection_list",
        "window_size",
        "gizmo_entity_uid",
        "selected_entity_uid",
        "selected_entity_init_distance_to_cam",
        "loading_functions",
        "loading_tasks"
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

        self.window_size = None
        self.entity_ray_intersection_list = []
        self.gizmo_entity_uid = None
        self.loading_tasks = []

        # DEBUG
        self.selected_entity_uid = None
        self.selected_entity_init_distance_to_cam = None

    def initialise(self) -> bool:

        return True

    def on_event(self, event_type: int, event_data: tuple):

        if event_type == constants.EVENT_WINDOW_DROP_FILES:

            for fpath in event_data:
                directory, filename = os.path.split(fpath)
                filename_no_ext, extension = os.path.splitext(filename)
                extension_clean = extension.lower().strip(".")

                if extension_clean not in ImportSystem.LOADING_TASK_CLASS:
                    self.logger.warning(f"Extension .{extension_clean} not supported")
                    continue

                new_loading_task = ImportSystem.LOADING_TASK_CLASS[extension_clean](fpath=fpath)
                new_loading_task.start()
                self.loading_tasks.append(new_loading_task)

    def update(self, elapsed_time: float, context: moderngl.Context) -> bool:
        """
        At Each update, the progress of each loading task (thread) is checked and published

        :param elapsed_time:
        :param context:
        :return:
        """

        # Check on each of the tasks' progress
        tasks_to_remove = []
        for loading_task in self.loading_tasks:
            if not loading_task.is_alive():
                tasks_to_remove.append(loading_task)
            else:
                print(f"Loading file {loading_task.fpath}: {loading_task.task_progress}%")
                if loading_task.task_completed:
                    tasks_to_remove.append(loading_task)
                if loading_task.task_crashed:
                    print("Task Failed")
                    tasks_to_remove.append(loading_task)

        # Remove any tasks that are complete or crashed
        for loading_task in tasks_to_remove:
            loading_task.join()
            self.loading_tasks.remove(loading_task)

        return True
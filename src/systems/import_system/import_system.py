import logging
import os.path

import moderngl

from src.core import constants
from src.systems.system import System
from src.core.event_publisher import EventPublisher
from src.core.action_publisher import ActionPublisher
from src.core.scene import Scene

from src.systems.import_system.loading_task import FileDataInterface
from src.systems.import_system.loading_task_obj import LoadingTaskObj
from src.systems.import_system.loading_task_gltf import LoadingTaskGLTF


class ImportSystem(System):

    name = "import_system"

    LOADING_TASK_CLASS = {
        "obj": LoadingTaskObj,
        "gltf": LoadingTaskGLTF,
        "bin": LoadingTaskGLTF
    }

    __slots__ = [
        "entity_ray_intersection_list",
        "window_size",
        "gizmo_entity_uid",
        "selected_entity_uid",
        "selected_entity_init_distance_to_cam",
        "loading_functions",
        "loading_tasks",
        "file_interfaces"
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.window_size = None
        self.entity_ray_intersection_list = []
        self.gizmo_entity_uid = None
        self.loading_tasks = []
        self.file_interfaces = {}

        # DEBUG
        self.selected_entity_uid = None
        self.selected_entity_init_distance_to_cam = None

    def initialise(self) -> bool:

        return True

    def on_event(self, event_type: int, event_data: tuple):

        if event_type == constants.EVENT_WINDOW_DROP_FILES:

            for absolute_fpath in event_data:

                directory, filename = os.path.split(absolute_fpath)
                filename_no_ext, extension = os.path.splitext(filename)
                extension_no_period = extension.lower().strip(".")

                # Safety first
                if extension_no_period not in ImportSystem.LOADING_TASK_CLASS:
                    self.logger.warning(f"Extension .{extension_no_period} not supported")
                    continue

                # Now you can load the file
                new_loading_task = ImportSystem.LOADING_TASK_CLASS[extension_no_period](fpath=absolute_fpath)
                new_loading_task.start()
                self.loading_tasks.append(new_loading_task)
                self.logger.debug(f"Loading task created : {new_loading_task.fpath}")

    def process_obj_data(self, file_interface: FileDataInterface):

        pass

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

            if loading_task.task_completed:
                self.file_interfaces[loading_task.fpath] = loading_task.file_data_interface.data
                tasks_to_remove.append(loading_task)
                self.logger.debug(f"Loading task successfully : {loading_task.fpath}")

            if loading_task.task_crashed:
                self.logger.error(f"Loading task failed : {loading_task.fpath}")
                tasks_to_remove.append(loading_task)

        # Remove any tasks that are complete or crashed
        for loading_task in tasks_to_remove:
            loading_task.join()
            self.loading_tasks.remove(loading_task)
            self.logger.debug(f"Loading task removed : {loading_task.fpath}")

        return True
import time
from dataclasses import dataclass
import threading
from typing import Union, Any


@dataclass
class FileDataInterface:
    interface_type: str = "",
    loaded: bool = False,
    open: bool = False,
    streamable: bool = False,
    data: Any = None


class LoadingTask(threading.Thread):
    def __init__(self, fpath: str):
        super().__init__()
        self.fpath = fpath
        self.file_data_interface = None
        self.task_completed = False
        self.task_crashed = False
        self.start_time = time.perf_counter()
        self.stop_time = self.start_time

    def load_file(self, fpath: str) -> bool:
        self.task_completed = True
        return True

    def time_alive(self):
        return time.perf_counter() - self.start_time

    def run(self):
        # Main thread loop. Do not get rid of this!
        try:
            self.task_completed = self.load_file(fpath=self.fpath)
            self.stop_time = time.perf_counter()

        except Exception as e:
            self.task_crashed = True
            raise Exception(f"Failed to load file {self.fpath}: {str(e)}")
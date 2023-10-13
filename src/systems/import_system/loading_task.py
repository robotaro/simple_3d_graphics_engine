import threading


class LoadingTask(threading.Thread):
    def __init__(self, fpath: str):
        super().__init__()
        self.fpath = fpath
        self.task_progress = 0
        self.task_completed = False
        self.task_crashed = False

    def load_file(self, fpath: str) -> bool:
        self.task_progress = 100
        return True

    def run(self):
        try:
            self.task_completed = self.load_file(fpath=self.fpath)

        except Exception as e:
            self.task_crashed = True
            print(f"Failed to load file {self.fpath}: {str(e)}")
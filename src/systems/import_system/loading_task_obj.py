from src.systems.import_system.loading_task import LoadingTask
from src.utilities import utils_mesh_3d


class LoadingTaskObj(LoadingTask):
    
    def __init__(self, fpath):
        super().__init__(fpath=fpath)

    def load_file(self, fpath: str) -> bool:
        vertices, normals, uvs, indices = utils_mesh_3d.from_obj(fpath=fpath)
        self.task_progress = 100
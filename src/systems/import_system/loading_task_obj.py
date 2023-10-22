from src.systems.import_system.loading_task import LoadingTask, FileDataInterface
from src.utilities import utils_mesh_3d


class LoadingTaskObj(LoadingTask):
    
    def __init__(self, fpath):
        super().__init__(fpath=fpath)

    def load_file(self, fpath: str) -> bool:

        vertices, normals, uvs, indices = utils_mesh_3d.from_obj(fpath=fpath)

        mesh_data = dict()
        mesh_data["vertices"] = vertices
        mesh_data["normals"] = normals
        mesh_data["uvs"] = uvs
        mesh_data["indices"] = indices

        self.file_data_interface = FileDataInterface(
            interface_type="obj",
            loaded=True,
            data=mesh_data)

        return True

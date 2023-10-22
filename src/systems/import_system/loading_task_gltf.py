from pygltflib import GLTF2

from src.systems.import_system.loading_task import LoadingTask, FileDataInterface


class LoadingTaskGLTF(LoadingTask):

    def __init__(self, fpath):
        super().__init__(fpath=fpath)
        self.gltf_scene = None

    def load_file(self, fpath: str) -> bool:

        gltf_scene = GLTF2().load(fpath)

        # TODO: This is just a simple placeholder to load all meshes from the gltf file

        entity_blueprint = {}


        self.file_interface = FileDataInterface(
            interface_type="gltf",
            loaded=True,
            open=False,
            streamable=False,
            data=entity_blueprint)
        return True

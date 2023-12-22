import os
import logging

from src.core.file_loaders.file_loader_obj import FileLoaderOBJ
from src.core.file_loaders.file_loader_bvh import FileLoaderBVH
from src.core.file_loaders.file_loader_gltf import FileLoaderGLTF
from src.core.file_loaders.file_loader_mesh_blueprint import FileLoaderMeshBlueprint


class DataManager:

    """
    A simple class designed to manage blocks of data utilised by any system that or plugins.
    Any data that needs to be manipulated and saved to the disk should use this manager
    """

    __slots__ = [
        "logger",
        "data_groups",
        "file_loaders"
    ]

    def __init__(self, logger: logging.Logger):

        self.logger = logger
        self.data_groups = {}
        self.file_loaders = {
            ".obj": FileLoaderOBJ(all_resources=self.data_groups),
            ".bvh": FileLoaderBVH(all_resources=self.data_groups),
            ".gltf": FileLoaderGLTF(all_resources=self.data_groups),
            ".glb": FileLoaderGLTF(all_resources=self.data_groups),
            ".mesh_blueprint": FileLoaderMeshBlueprint(all_resources=self.data_groups)
        }

    def load_file(self, data_group_id: str, fpath: str) -> bool:

        _, extension = os.path.splitext(fpath)

        loader = self.file_loaders.get(extension, None)
        if loader is None:
            raise Exception(f"Extension '{extension}' not currently supported")

        # Execute main loading operation here
        return loader.load(resource_uid=data_group_id, fpath=fpath)

    def add_data_group(self, data_group_id: str, data_group: dict, overwrite=True):

        if not overwrite and data_group_id in self.data_groups:
            raise ValueError(f"[ERROR] DataGroup ID {data_group_id} already exists")

        self.data_groups[data_group_id] = data_group



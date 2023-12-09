import os
import logging

# Resource loaders
from src.core.resource_loaders.resource_loader_obj import ResourceLoaderOBJ
from src.core.resource_loaders.resource_loader_bvh import ResourceLoaderBVH
from src.core.resource_loaders.resource_loader_gltf import ResourceLoaderGLTF

from src.utilities import utils_obj, utils_bvh_reader, utils_gltf, utils_gltf_reader


class ResourceManager:

    __slots__ = [
        "logger",
        "resources",
        "resource_loaders"]

    def __init__(self, logger: logging.Logger):

        self.logger = logger
        self.resources = {}
        self.resource_loaders = {
            ".obj": ResourceLoaderOBJ(all_resources=self.resources),
            ".bvh": ResourceLoaderBVH(all_resources=self.resources),
            ".gltf": ResourceLoaderGLTF(all_resources=self.resources),
            ".glb": ResourceLoaderGLTF(all_resources=self.resources)}

    def load_resource(self, resource_uid: str, fpath: str) -> bool:

        _, extension = os.path.splitext(fpath)

        loader = self.resource_loaders.get(extension, None)
        if loader is None:
            raise Exception(f"Extension '{extension}' not currently supported")

        # Execute main loading operation here
        return loader.load(resource_uid=resource_uid, fpath=fpath)

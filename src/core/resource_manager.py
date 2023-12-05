import os
import logging

# Resource loaders
from src.core.resource_loaders.resource_loader_obj import ResourceLoaderOBJ
from src.core.resource_loaders.resource_loader_bvh import ResourceLoaderBVH

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
            ".bvh": ResourceLoaderBVH(all_resources=self.resources)
        }

    def load_resource(self, resource_uid: str, fpath: str) -> bool:

        _, extension = os.path.splitext(fpath)

        loader = self.resource_loaders.get(extension, None)
        if loader is None:
            self.logger.error(f"Extension '{extension}' not currently supported")
            return False

        # Execute main loading operation here
        return loader.load(resource_uid=resource_uid, fpath=fpath)

    def load_gltf(self, resource_uid: str, fpath: str) -> None:

        """
        This function operates a little differently form other resource loading funcitons. Given that the
        GLTF standard can hold many different types of data, each type of data is loaded as a separate
        resource. For example, each mesh will be its own MESH resource, node animation will be a SKELETON resource,
        etc. All resources will be named under the provide resource_uid group like "provided_uid/NEW_RESOURCE"
        :param resource_uid: string, unique identified for all ersources
        :param fpath:
        :return: None
        """

        gltf_reader = utils_gltf_reader.GLTFreader()
        gltf_reader.load(gltf_fpath=fpath)




        g = 0
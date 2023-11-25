import os
import logging
import numpy as np

# Specifuc libraries for certain extensions
import trimesh

from src.core import constants
from src.core.data_block import DataBlock

from src.utilities import utils_obj



class Resource:

    __slots__ =[
        "data_blocks"
    ]

    def __init__(self):
        self.data_blocks = {}


class ResourceManager:

    __slots__ = [
        "logger",
        "resources",
        "extension_handlers"
    ]

    def __init__(self, logger: logging.Logger):

        self.logger = logger
        self.resources = {}
        self.extension_handlers = {
            "obj": self.load_obj,
        }

    def load(self, resource_uid: str, fpath: str):

        _, extension = os.path.splitext(fpath)
        extension_no_dot = extension.strip(".")

        handler = self.extension_handlers.get(extension_no_dot, None)
        if handler is None:
            self.logger.error(f"Extension '{extension}' not currently supported")
            return

        self.resources[resource_uid] = handler(fpath)

    def load_obj(self, fpath: str) -> Resource:
        mesh = trimesh.load(fpath)

        new_resource = Resource()

        new_resource.data_blocks["vertices"] = DataBlock(
            data_shape=mesh.vertices.shape,
            data_type=np.float32,
            data_format=constants.DATA_BLOCK_FORMAT_VEC3)
        new_resource.data_blocks["vertices"].data[:] = mesh.vertices

        new_resource.data_blocks["normals"] = DataBlock(
            data_shape=mesh.vertex_normals.shape,
            data_type=mesh.vertex_normals.dtype,
            data_format=constants.DATA_BLOCK_FORMAT_VEC3)
        new_resource.data_blocks["normals"].data[:] = mesh.vertices

        new_resource.data_blocks["faces"] = DataBlock(
            data_shape=mesh.faces.shape,
            data_type=np.int32,
            data_format=constants.DATA_BLOCK_FORMAT_VEC3)
        new_resource.data_blocks["faces"].data[:] = mesh.faces

        if "uv" in mesh.visual.__dict__:
            new_resource.data_blocks["uv"] = DataBlock(
                data_shape=mesh.visual.uv.shape,
                data_type=np.float32,
                data_format=constants.DATA_BLOCK_FORMAT_VEC2)
            new_resource.data_blocks["uv"].data[:] = mesh.visual.uv

        return new_resource


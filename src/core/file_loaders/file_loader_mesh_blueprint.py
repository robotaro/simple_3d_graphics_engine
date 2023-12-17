import json

from src.core import constants
from src.core.data_block import DataBlock
from src.core.data_group import DataGroup
from src.core.file_loaders.file_loader import FileLoader
from src.systems.render_system.mesh_factory_3d import MeshFactory3D


class FileLoaderMeshBlueprint(FileLoader):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def load(self, resource_uid: str, fpath: str) -> bool:
        mesh_factory = MeshFactory3D()

        with open(fpath) as file:
            shape_list = json.load(file)
            new_mesh = mesh_factory.generate_mesh(shape_list=shape_list)

            new_resource = DataGroup(archetype=constants.RESOURCE_TYPE_MESH)
            new_resource.data_blocks["vertices"] = DataBlock(data=new_mesh["vertices"])
            new_resource.data_blocks["normals"] = DataBlock(data=new_mesh["normals"])
            new_resource.data_blocks["colors"] = DataBlock(data=new_mesh["colors"])
            if new_mesh["indices"] is not None:
                new_resource.data_blocks["indices"] = DataBlock(data=new_mesh["indices"])

            self.external_data_groups[f"{resource_uid}/mesh_0"] = new_resource

            return True

import trimesh

from src.core import constants
from src.core.data_block import DataBlock
from src.core.data_group import DataGroup
from src.core.file_loaders.file_loader import FileLoader


class FileLoaderOBJ(FileLoader):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def load(self, resource_uid: str, fpath: str) -> bool:
    
        mesh = trimesh.load(fpath)

        new_resource = DataGroup(archetype=constants.RESOURCE_TYPE_MESH)
        new_resource.data_blocks["vertices"] = DataBlock(data=mesh.vertices)
        new_resource.data_blocks["normals"] = DataBlock(data=mesh.vertex_normals)
        new_resource.data_blocks["indices"] = DataBlock(data=mesh.faces)
    
        if "uv" in mesh.visual.__dict__:
            new_resource.data_blocks["uv"] = DataBlock(data=mesh.visual.uv)

        self.external_data_groups[f"{resource_uid}/mesh_0"] = new_resource

        return True

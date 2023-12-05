import trimesh

from src.core import constants
from src.core.resource_loaders.resource import Resource
from src.core.data_block import DataBlock
from src.core.resource_loaders.resource_loader import ResourceLoader


class ResourceLoaderOBJ(ResourceLoader):
    
    def __init__(self, all_resources: dict):
        super().__init__(all_resources=all_resources)
    
    def load(self, resource_uid: str, fpath: str) -> bool:
    
        mesh = trimesh.load(fpath)

        new_resource = Resource(resource_type=constants.RESOURCE_TYPE_MESH)
        new_resource.data_blocks["vertices"] = DataBlock(data=mesh.vertices)
        new_resource.data_blocks["normals"] = DataBlock(data=mesh.vertex_normals)
        new_resource.data_blocks["faces"] = DataBlock(data=mesh.faces)
    
        if "uv" in mesh.visual.__dict__:
            new_resource.data_blocks["uv"] = DataBlock(data=mesh.visual.uv)

        complete_id = f"{resource_uid}/mesh_0"

        self.all_resources[complete_id] = new_resource

        return True

from src.core import constants
from src.core.resource_loaders.resource import Resource
from src.core.data_block import DataBlock
from src.core.resource_loaders.resource_loader import ResourceLoader

from src.utilities import utils_gltf_reader


class ResourceLoaderGLTF(ResourceLoader):

    def __init__(self, all_resources: dict):
        super().__init__(all_resources=all_resources)

    def load(self, resource_uid: str, fpath: str) -> bool:
        gltf_reader = utils_gltf_reader.GLTFreader()
        gltf_reader.load(gltf_fpath=fpath)

        for mesh_index, mesh in enumerate(gltf_reader.get_all_meshes()):

            new_resource = Resource(resource_type=constants.RESOURCE_TYPE_MESH)
            new_resource.metadata["render_mode"] = mesh["render_mode"]
            mesh_attrs = mesh["attributes"]

            if "indices" in mesh:
                new_resource.data_blocks["indices"] = DataBlock(data=mesh["indices"])

            if "POSITION" in mesh_attrs:
                new_resource.data_blocks["vertices"] = mesh_attrs["POSITION"]

            if "NORMAL" in mesh_attrs:
                new_resource.data_blocks["normals"] = mesh_attrs["NORMAL"]

            self.all_resources[f"{resource_uid}/mesh_{mesh_index}"] = new_resource

        return True

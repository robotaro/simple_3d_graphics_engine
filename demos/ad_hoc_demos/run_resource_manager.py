import logging
from src.core.resource_manager import ResourceManager


if __name__ == "__main__":

    logger = logging.Logger(name="Demo Resource Manager")
    manager = ResourceManager(logger=logger)

    manager.load(resource_uid="dragon",
                 fpath=r"D:\git_repositories\alexandrepv\simple_3d_graphics_engine\resources\meshes\dragon.obj")
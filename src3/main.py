import sys
import os

path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(path)

from src3.io.gltf_reader import GLTFReader
from src3.app import App


def load_gltf():

    fpath = r"D:\git_repositories\alexandrepv\simple_3d_graphics_engine\resources\meshes\situp_to_iddle.gltf"

    reader = GLTFReader()
    reader.load(gltf_fpath=fpath)

    materials = reader.get_materials()
    meshes = reader.get_meshes()
    nodes = reader.get_nodes()
    animations = reader.get_animations()
    skeletons = reader.get_skeletons()


def main():

    #load_gltf()

    app = App(window_title="Basic Scene Demo", vertical_sync=False)
    app.run()


if __name__ == "__main__":
    main()

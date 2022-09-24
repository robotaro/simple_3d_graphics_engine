from core.engine import Engine
from utilities import utils_gltf

def run():

    glb_fpath = r"D:\Dropbox\Xande and Jane Sharefolder\3D Sketchfab models\Nara The Desert Dancer (Free download)\nara_the_desert_dancer_free_download.glb"

    gltf_loader = utils_gltf.GLFTLoader()
    gltf_loader.load(glb_fpath)
    scenes = gltf_loader.get_scene_dicts()


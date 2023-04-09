from core.engine import Engine
from utilities import utils_gltf

def main():

    glb_fpath = r"D:\Dropbox\Xande and Jane Sharefolder\3D Sketchfab models\Nara The Desert Dancer (Free download)\nara_the_desert_dancer_free_download.glb"
    gltf_blueprint = utils_gltf.load_gltf_to_blueprint(fpath=glb_fpath)

    app = Engine()
    app.main_scene.from_gltf_blueprint(blueprint=gltf_blueprint)
    app.run()


if __name__ == "__main__":

    main()

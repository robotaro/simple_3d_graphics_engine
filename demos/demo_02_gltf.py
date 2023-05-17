from core.engine import Engine
from utilities import utils_gltf
import os

def main():

    path_parts = ["data", "models", "Fox7cc12qk5uw399hqw.gltf"]
    glb_fpath = os.path.join(*path_parts)
    gltf_blueprint = utils_gltf.load_gltf_to_blueprint(fpath=glb_fpath)

    app = Engine()
    app.main_scene.from_gltf_blueprint(blueprint=gltf_blueprint)
    app.run()


if __name__ == "__main__":

    main()

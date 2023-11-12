from src.core.data_management.loader_gltf2 import LoaderGLTF2


def main():

    loader = LoaderGLTF2()
    fpath = r"D:\git_repositories\alexandrepv\simple_3d_graphics_engine\resources\meshes\BrainStem.gltf"
    #fpath = r"D:\3d_models\gltf_models\glTF-Sample-Models-master\2.0\Sponza\glTF\Sponza.gltf"
    #output = loader.load_glb(glb_fpath=fpath)
    output = loader.load(gltf_fpath=fpath)
    g = 0


if __name__ == "__main__":

    main()
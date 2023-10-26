from src.core.data_management.loader_gltf2 import LoaderGLTF2


def main():

    loader = LoaderGLTF2()
    fpath = r"D:\git_repositories\alexandrepv\simple_3d_graphics_engine\resources\meshes\BrainStem.gltf"
    #output = loader.load_glb(glb_fpath=fpath)
    output = loader.load_gltf(gltf_fpath=fpath)
    g = 0


if __name__ == "__main__":

    main()
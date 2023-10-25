from src.core.data_management.loader_gltf2 import LoaderGLTF2


def main():

    loader = LoaderGLTF2()
    output = loader.load(fpath=r"D:\3d_models\gltf_models\glTF-Sample-Models-master\2.0\BrainStem\glTF\BrainStem.gltf")


if __name__ == "__main__":

    main()
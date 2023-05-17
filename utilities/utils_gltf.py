import os
from pygltflib import GLTF2, BufferFormat
import struct
import numpy as np
import copy

VERTEX_UNIT_SIZE_BYTES = 4


def extract_nodes(gltf_obj: GLTF2) -> dict:

    nodes = dict()
    for index, node in enumerate(gltf_obj.nodes):
        nodes[index] = {"name": node.name,
                        "mesh_index": node.mesh,
                        "child_indices": node.children,
                        "rotation": node.rotation,
                        "translation": node.translation,
                        "scale": node.scale,
                        "matrix": node.matrix}

        if node.matrix is not None:
            nodes[index]['matrix'] = np.array(node.matrix, dtype=np.float32).reshape(4, -1)

    return nodes

def extract_scenes(gltf_obj: GLTF2) -> dict:

    scenes = dict()
    for index, scene in enumerate(gltf_obj.scenes):
        scenes[index] = {"name": scene.name,
                         "root_node_index": scene.nodes[0]}

    return scenes


def extract_materials(gltf_obj: GLTF2) -> dict:

    materials = dict()
    for index, material in enumerate(gltf_obj.materials):
        materials[index] = {"name": material.name,
                            "alpha_mode": material.alphaMode,
                            "alpha_cutoff": material.alphaCutoff,
                            "emissive_factor": material.emissiveFactor,
                            "emissive_texture": material.emissiveTexture,
                            "normal_texture": material.normalTexture,
                            "occlusion_texture": material.occlusionTexture,
                            "double_sided": material.doubleSided,
                            "pbr_metallic_roughness": material.pbrMetallicRoughness,
                            "extensions": copy.deepcopy(material.extensions)}
    return materials


def extract_array_from_buffer(gltf_obj, accessor, output_dtype=np.float32):

    # get the binary data for this mesh primitive from the buffer
    bufferView = gltf_obj.bufferViews[accessor.bufferView]
    buffer = gltf_obj.buffers[bufferView.buffer]
    data = gltf_obj.get_data_from_buffer_uri(buffer.uri)
    data_format = f"<{''.join('f' for _ in range(bufferView.byteStride // VERTEX_UNIT_SIZE_BYTES))}"

    # Pull each vertex from the binary buffer and convert it into a tuple of python floats
    vertices = []
    for i in range(accessor.count):
        index = bufferView.byteOffset + accessor.byteOffset + i * bufferView.byteStride
        d = data[index:index + bufferView.byteStride]
        vertex = struct.unpack(data_format, d)  # convert from little-endian base64 to N floats
        vertices.append(vertex)

    # Convert primitive back to
    return np.array(vertices, dtype=output_dtype)


def extract_meshes(gltf_obj: GLTF2) -> dict:

    # Original code from: https://pypi.org/project/pygltflib/

    meshes = dict()
    for mesh_index, mesh in enumerate(gltf_obj.meshes):

        primitives = dict()
        for primitive_index, primitive in enumerate(mesh.primitives):

            new_primitive = dict()
            for attribute_name in primitive.attributes.__dict__:
                attribute = eval(f"primitive.attributes.{attribute_name}")
                if attribute is None:
                    continue
                accessor = gltf_obj.accessors[attribute]
                data_array = extract_array_from_buffer(gltf_obj=gltf_obj, accessor=accessor)
                new_primitive[attribute_name] = data_array

            primitives[primitive_index] = new_primitive

        meshes[mesh_index] = {
            "primitives": primitives,
            "node_index": 45  # TODO: Figure out why?
        }

    return meshes


def load_gltf_to_blueprint(fpath: str) -> dict:

    """
    This function reads both .gltf and .glb file formats
    :param gltf_fpath:
    :return:
    """
    try:
        gltf_obj = GLTF2().load(fpath)
    except:
        raise Exception(f"[ERROR] Failed to load '{fpath}'")

    file_dict = dict()
    file_dict['nodes'] = extract_nodes(gltf_obj=gltf_obj)
    file_dict['materials'] = extract_materials(gltf_obj=gltf_obj)
    file_dict['meshes'] = extract_meshes(gltf_obj=gltf_obj)
    file_dict['scenes'] = extract_scenes(gltf_obj=gltf_obj)

    return file_dict

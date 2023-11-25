import numpy as np


def load_obj(fpath: str):
    raw_vertices = []
    raw_normals = []
    raw_uvs = []
    faces = []

    with open(fpath, 'r') as file:
        for line in file:
            parts = [valid_part for valid_part in line.strip().split(' ') if len(valid_part) > 0]
            if parts[0] == 'v':
                raw_vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif parts[0] == 'vn':
                raw_normals.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif parts[0] == 'vt':
                raw_uvs.append([float(parts[1]), float(parts[2])])
            elif parts[0] == 'f':
                try:
                    face_data = [tuple(map(int, p.split('//'))) for p in parts[1:] if len(p) > 0]
                except Exception:
                    g = 0
                faces.append(face_data)

    indexed_vertices = []
    indexed_normals = []
    indexed_uvs = []
    indices = []

    for face in faces:
        for v_idx, vt_idx, vn_idx in face:
            indexed_vertices.append(raw_vertices[v_idx - 1])
            indexed_uvs.append(raw_uvs[vt_idx - 1] if vt_idx else [0, 0])
            indexed_normals.append(raw_normals[vn_idx - 1] if vn_idx else [0, 0, 0])
            indices.append(len(indexed_vertices) - 1)

    vertices = np.array(indexed_vertices, dtype=np.float32)
    normals = np.array(indexed_normals, dtype=np.float32)
    uvs = np.array(indexed_uvs, dtype=np.float32)
    indices = np.array(indices, dtype=np.int32).reshape(-1, 3)

    return vertices, normals, uvs, indices
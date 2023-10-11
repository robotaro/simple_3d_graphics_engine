from numba import njit
import numpy as np
import trimesh.transformations as transformations


def matrix2translation(m):
    return m[:3 ,3]


def matrix2rotation(m):
    U = m[:3 ,:3]
    norms = np.linalg.norm(U.T, axis=1)
    return U / norms


def matrix2quaternion(m):
    M = np.eye(4)
    M[:3 ,:3] = matrix2rotation(m)
    q_wxyz = transformations.quaternion_from_matrix(M)
    return np.roll(q_wxyz, -1)


def matrix2scale(m):
    return np.linalg.norm(m[:3 ,:3].T, axis=1)


def quaternion2rotation(q):
    q_wxyz = np.roll(q, 1)
    return transformations.quaternion_matrix(q_wxyz)[:3 ,:3]


def tqs2matrix(translation: np.array, quaternion: np.array, scale: np.array):
    S = np.eye(4)
    S[:3, :3] = np.diag(scale)

    R = np.eye(4)
    R[:3, :3] = quaternion2rotation(quaternion)

    T = np.eye(4)
    T[:3, 3] = translation

    return T.dot(R.dot(S))
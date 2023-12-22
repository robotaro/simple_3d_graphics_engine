from numba import njit
import numpy as np

from src.core import constants

@njit
def encode_command(layer, is_transparent, distance, material, mesh, transform, render_mode):
    command = (layer << constants.LAYER_SHIFT) | \
              (is_transparent << constants.TRANSPARENCY_SHIFT) | \
              (distance << constants.DISTANCE_SHIFT) | \
              (material << constants.MATERIAL_SHIFT) | \
              (mesh << constants.MESH_SHIFT) | \
              (transform << constants.TRANSFORM_SHIFT) | \
              (render_mode << constants.RENDER_MODE_SHIFT)
    return command

@njit
def decode_command(command):
    layer = (command >> constants.LAYER_SHIFT) & constants.LAYER_MASK
    is_transparent = (command >> constants.TRANSPARENCY_SHIFT) & constants.TRANSPARENCY_MASK
    distance = (command >> constants.DISTANCE_SHIFT) & constants.DISTANCE_MASK
    material = (command >> constants.MATERIAL_SHIFT) & constants.MATERIAL_MASK
    mesh = (command >> constants.MESH_SHIFT) & constants.MESH_MASK
    transform = (command >> constants.TRANSFORM_SHIFT) & constants.TRANSFORM_MASK
    render_mode = (command >> constants.RENDER_MODE_SHIFT) & constants.RENDER_MODE_MASK
    return layer, is_transparent, distance, material, mesh, transform, render_mode

@njit
def encode_distance(distance, max_distance):
    # Normalize distance based on the maximum distance
    normalized_distance = np.clip(distance / max_distance, 0, 1)
    # Encode into 10 bits
    encoded_distance = int(normalized_distance * (2 ** constants.DISTANCE_BITS - 1))
    return encoded_distance

@njit
def decode_distance(encoded_distance, max_distance):
    # Decode from 10 bits
    normalized_distance = encoded_distance / (2 ** constants.DISTANCE_BITS - 1)
    # Convert back to actual distance
    distance = normalized_distance * max_distance
    return distance

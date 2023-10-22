import logging

import pytest
import numpy as np

from src.core import constants
from src.core.component_pool import ComponentPool
from src.components.transform_3d import Transform3D
from src.components.mesh import Mesh


def test_constructor():

    logger = logging.getLogger('test_logger')
    pool = ComponentPool(logger=logger)
    assert pool.entity_uid_counter == constants.COMPONENT_POOL_STARTING_ID_COUNTER
    assert pool.entities == {}
    assert pool.transform_3d_components == {}
    assert pool.mesh_components == {}
    assert pool.camera_components == {}


def test_create_entity():

    logger = logging.getLogger('test_logger')
    pool = ComponentPool(logger=logger)

    new_entity_uid_1 = pool._create_entity()
    new_entity_uid_2 = pool._create_entity()
    new_entity_uid_3 = pool._create_entity()

    assert new_entity_uid_1 == constants.COMPONENT_POOL_STARTING_ID_COUNTER
    assert new_entity_uid_2 == constants.COMPONENT_POOL_STARTING_ID_COUNTER + 1
    assert new_entity_uid_3 == constants.COMPONENT_POOL_STARTING_ID_COUNTER + 2


def test_add_and_remove_components():

    logger = logging.getLogger('test_logger')
    pool = ComponentPool(logger=logger)

    entity_uid = pool._create_entity()

    parameters = {}

    # Add Components
    new_transform = pool.add_component(entity_uid=entity_uid,
                                       component_type=constants.COMPONENT_TYPE_TRANSFORM_3D,
                                       parameters=parameters)
    new_mesh = pool.add_component(entity_uid=entity_uid,
                                  component_type=constants.COMPONENT_TYPE_MESH,
                                  parameters=parameters)

    assert isinstance(new_transform, Transform3D)
    assert isinstance(new_mesh, Mesh)

    # Try to create another mesh, which should raise an exception
    with pytest.raises(TypeError) as excinfo:
        _ = pool.add_component(entity_uid=entity_uid, component_type=constants.COMPONENT_TYPE_MESH)

    # Get All Components
    result_components = pool.get_all_components(entity_uid=entity_uid)
    assert len(result_components) == 2  # Mesh and transforms
    # TODO: Check types in more detail

    # Get Single Component
    result_component = pool.get_component(entity_uid=entity_uid, component_type=constants.COMPONENT_TYPE_TRANSFORM_3D)
    target_transform = Transform3D(parameters=parameters)
    np.testing.assert_array_equal(result_component.world_matrix, target_transform.world_matrix)  # Mesh and transforms
    # TODO: Check types in more detail

    # Remove Component
    pool.remove_component(entity_uid=entity_uid, component_type=constants.COMPONENT_TYPE_TRANSFORM_3D)
    result_components = pool.get_all_components(entity_uid=entity_uid)
    assert len(result_components) == 1  # Mesh and transforms
    # TODO: Check types in more detail

    # Try to get removed component
    result_component = pool.get_component(entity_uid=entity_uid, component_type=constants.COMPONENT_TYPE_TRANSFORM_3D)
    assert result_component is None


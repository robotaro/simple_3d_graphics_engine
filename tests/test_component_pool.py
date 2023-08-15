import pytest
import numpy as np

from ecs import constants
from ecs.component_pool import ComponentPool
from ecs.components.transform import Transform
from ecs.components.mesh import Mesh


def test_constructor():

    pool = ComponentPool()
    assert pool.entity_uid_counter == 0
    assert pool.entities == {}
    assert pool.transform_components == {}
    assert pool.mesh_components == {}
    assert pool.renderable_components == {}
    assert pool.camera_components == {}


def test_create_entity():

    pool = ComponentPool()

    new_entity_uid_1 = pool.create_entity()
    new_entity_uid_2 = pool.create_entity()
    new_entity_uid_3 = pool.create_entity()

    assert new_entity_uid_2 == 1
    assert new_entity_uid_1 == 0
    assert new_entity_uid_3 == 2


def test_add_and_remove_components():

    pool = ComponentPool()

    entity_uid = pool.create_entity()

    # Add Components
    new_transform = pool.add_component(entity_uid=entity_uid,
                                       component_type=constants.COMPONENT_TYPE_TRANSFORM)
    new_mesh = pool.add_component(entity_uid=entity_uid,
                                  component_type=constants.COMPONENT_TYPE_MESH)

    assert isinstance(new_transform, Transform)
    assert isinstance(new_mesh, Mesh)

    # Try to create another mesh, which should raise an exception
    with pytest.raises(TypeError) as excinfo:
        _ = pool.add_component(entity_uid=entity_uid, component_type=constants.COMPONENT_TYPE_MESH)

    # Get All Components
    result_components = pool.get_all_components(entity_uid=entity_uid)
    assert len(result_components) == 2  # Mesh and transforms
    # TODO: Check types in more detail

    # Get Single Component
    result_component = pool.get_component(entity_uid=entity_uid, component_type=constants.COMPONENT_TYPE_TRANSFORM)
    target_transform = Transform()
    np.testing.assert_array_equal(result_component.local_matrix, target_transform.local_matrix)  # Mesh and transforms
    # TODO: Check types in more detail

    # Remove Component
    pool.remove_component(entity_uid=entity_uid, component_type=constants.COMPONENT_TYPE_TRANSFORM)
    result_components = pool.get_all_components(entity_uid=entity_uid)
    assert len(result_components) == 1  # Mesh and transforms
    # TODO: Check types in more detail

    # Try to get removed component
    result_component = pool.get_component(entity_uid=entity_uid, component_type=constants.COMPONENT_TYPE_TRANSFORM)
    assert result_component is None


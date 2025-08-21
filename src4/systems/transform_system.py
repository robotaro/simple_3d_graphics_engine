
from src4.systems.system import System
from src4.world import World
from src4.components.transform import Transform
from src4.components.hierarchy import Hierarchy


class TransformSystem(System):
    """Handles transform updates and hierarchy"""

    def __init__(self, world: World):
        super().__init__(world)

    def update(self, delta_time: float):
        # Process hierarchy changes first
        self.process_dirty_entities("hierarchy", self._update_hierarchy)

        # Process transform changes
        self.process_dirty_entities("transform", self._update_transform)

    def _update_hierarchy(self, entity_id: int):
        """Update entity hierarchy relationships"""
        hierarchy = self.world.get_component(entity_id, Hierarchy)
        if not hierarchy:
            return

        # Update children's parent references
        for child_id in hierarchy.children_ids:
            child_hierarchy = self.world.get_component(child_id, Hierarchy)
            if child_hierarchy and child_hierarchy.parent_id != entity_id:
                child_hierarchy.parent_id = entity_id
                # Mark child as needing transform update
                self.world.mark_dirty(child_id, ["transform"])

    def _update_transform(self, entity_id: int):
        """Update entity transform and propagate to children"""
        transform = self.world.get_component(entity_id, Transform)
        if not transform:
            return

        # Calculate local matrix
        local_matrix = self._calculate_local_matrix(transform)

        # Get parent's world matrix if exists
        hierarchy = self.world.get_component(entity_id, Hierarchy)
        if hierarchy and hierarchy.parent_id:
            parent_transform = self.world.get_component(hierarchy.parent_id, Transform)
            if parent_transform and parent_transform.world_matrix is not None:
                # Parent has a valid world matrix, multiply with local
                transform.world_matrix = parent_transform.world_matrix @ local_matrix
            else:
                # Parent exists but no world matrix yet, just use local
                transform.world_matrix = local_matrix
        else:
            # No parent, world matrix is same as local matrix
            transform.world_matrix = local_matrix

        # Propagate to children
        if hierarchy:
            for child_id in hierarchy.children_ids:
                self.world.mark_dirty(child_id, ["transform"])

    def _calculate_local_matrix(self, transform: Transform):
        """Calculate local transformation matrix"""
        import numpy as np
        from math import cos, sin, radians

        # Create identity matrix
        matrix = np.eye(4, dtype='f4')

        # Apply translation
        matrix[0:3, 3] = transform.position

        # Apply rotation (simplified Euler angles - you'd use proper rotation matrix)
        # This is a basic implementation - use glm or a proper math library for production
        rx, ry, rz = [radians(angle) for angle in transform.rotation]

        # Rotation around X
        rot_x = np.array([
            [1, 0, 0, 0],
            [0, cos(rx), -sin(rx), 0],
            [0, sin(rx), cos(rx), 0],
            [0, 0, 0, 1]
        ], dtype='f4')

        # Rotation around Y
        rot_y = np.array([
            [cos(ry), 0, sin(ry), 0],
            [0, 1, 0, 0],
            [-sin(ry), 0, cos(ry), 0],
            [0, 0, 0, 1]
        ], dtype='f4')

        # Rotation around Z
        rot_z = np.array([
            [cos(rz), -sin(rz), 0, 0],
            [sin(rz), cos(rz), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype='f4')

        # Apply scale
        scale_matrix = np.diag([transform.scale[0], transform.scale[1], transform.scale[2], 1.0]).astype('f4')

        # Combine transformations: T * Rz * Ry * Rx * S
        rotation = rot_z @ rot_y @ rot_x
        matrix = matrix @ rotation @ scale_matrix

        return matrix

    def get_world_matrix(self, entity_id: int):
        """Get world matrix for an entity"""
        transform = self.world.get_component(entity_id, Transform)
        return transform.world_matrix if transform else None
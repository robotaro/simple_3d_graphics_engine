import numpy as np
import moderngl
import logging

from ecs.component_pool import ComponentPool
from ecs.systems.system import System
from ecs.event_publisher import EventPublisher
from ecs.action_publisher import ActionPublisher
from ecs.math import mat4

# DEBUG
import random


class TransformSystem(System):

    _type = "transform_system"

    __slots__ = [
        "update_tree",
        "entity_uid_update_order"
    ]

    def __init__(self, logger: logging.Logger,
                 component_pool: ComponentPool,
                 event_publisher: EventPublisher,
                 action_publisher: ActionPublisher):
        super().__init__(logger=logger,
                         component_pool=component_pool,
                         event_publisher=event_publisher,
                         action_publisher=action_publisher)

        self.entity_uid_update_order = []  # Ordered as a DAG
        self.update_tree = True

    def initialise(self, parameters: dict) -> bool:

        return True

    def update(self, elapsed_time: float, context: moderngl.Context) -> bool:

        if self.update_tree:
            self.recreate_transform_tree()
            self.update_tree = False

        for entity_uid in self.entity_uid_update_order:

            entity = self.component_pool.entities[entity_uid]
            transform = self.component_pool.transform_3d_components[entity_uid]

            if transform.dirty:
                transform.local_matrix = mat4.compute_transform(position=transform.position,
                                                                rotation_rad=transform.rotation,
                                                                scale=transform.scale[0])
                transform.dirty = False

            if entity.parent_uid is None:
                transform.world_matrix = transform.local_matrix
                continue

            # TODO: Think of a way to minimise unecessary updates. Probably do it when we move to DOD
            parent_transform = self.component_pool.transform_3d_components[entity.parent_uid]
            transform.world_matrix = parent_transform.world_matrix @ transform.local_matrix

        # ================= Process actions =================

        self.select_next_action()
        if self.current_action is None:
            return True

        return True

    def recreate_transform_tree(self):

        temp_update_order = []

        # Populate list out-of-order
        uid2index = {}
        for index, (entity_uid, entity) in enumerate(self.component_pool.entities.items()):
            #uid_map[entity_uid] = index
            temp_update_order.append((entity_uid, entity.parent_uid if entity.parent_uid is not None else -1))

        # TODO: REMOVE BLOODY SHUFFLE AND ORGANISE THIS!!

        # DEBUG
        random.seed(42)
        random.shuffle(temp_update_order)
        for index, (entity_uid, entity) in enumerate(temp_update_order):
            uid2index[entity_uid] = index

        order_array = np.array(temp_update_order, dtype=np.int32)


        # Sort list so that no child is updated before its parent
        for index in range(order_array.shape[0]):
            print(f"[{index}] ", end="")

            entity_uid = order_array[index, 0]
            parent_uid = order_array[index, 1]

            if parent_uid == -1:
                print(f" parent is -1")
                continue

            # Ir parent comes after the child, swap them
            while uid2index[parent_uid] > index:

                parent_index = uid2index[parent_uid]

                print(f" ({order_array[index, 0]}, {order_array[index, 1]}) <-> ({order_array[parent_index, 0]}, {order_array[parent_index, 1]})")
                temp = order_array[index, :].copy()
                order_array[index, :] = order_array[parent_index, :].copy()
                order_array[parent_index, :] = temp

                uid2index[entity_uid] = parent_index
                uid2index[parent_uid] = index
                break

        # Now we can get rid of the map
        self.entity_uid_update_order = order_array[:, 0].tolist()

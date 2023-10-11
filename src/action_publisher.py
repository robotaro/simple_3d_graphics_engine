import logging

from ecs import constants


class ActionPublisher:

    __slots__ = [
        "logger",
        "listeners"
    ]

    def __init__(self, logger: logging.Logger):

        self.logger = logger

        # Do it manually here to avoid having to check at every publish() call
        self.listeners = {
            constants.ACTION_TRANSFORM_LOOK_AT: [],
        }

    def subscribe(self, action_type: int, listener):
        self.listeners[action_type].append(listener)

    def unsubscribe(self, action_type, listener):
        if listener in self.listeners[action_type]:
            self.listeners[action_type].remove(listener)

    def publish(self, action_type: int, action_data: tuple, entity_id: int, component_type: int, sender):

        for listener in self.listeners[action_type]:

            # Prevent a sender to publishing to itself and creating a potential infinite loop
            if sender == listener:
                continue

            listener.on_action(action_type=action_type,
                               action_data=action_data,
                               entity_id=entity_id,
                               component_type=component_type)
import logging

import moderngl

from itertools import accumulate


class UBOInstance:

    __slots__ = [
        "ubo",
        "offsets",
        "binding_point"
    ]

    def __init__(self, ubo: moderngl.Buffer, offsets: dict, binding_point: int):
        self.ubo = ubo
        self.offsets = offsets
        self.binding_point = binding_point

    def bind(self):
        self.ubo.bind_to_uniform_block(self.binding_point)


class UBOManager:

    def __init__(self, logger: logging.Logger, ctx: moderngl.Context):
        self.logger = logger
        self.ctx = ctx
        self.ubos = {}

    def register_ubo(self, ubo_id: str, binding_point: int, variable_names_and_sizes: list) -> None:
        """
        [GLSL]
        layout (std140, binding = 0) uniform UBO_MVP {
            mat4 m_proj;
            mat4 m_view;
            mat4 m_model;
        };

        The UBO above can be defined as

        [Python]
            register_ubo(
                ubo_id="mvp",
                variable_names_and_sizes=[
                    ("m_proj", 64),
                    ("m_view", 64),
                    ("m_model", 64),
                ]
            )

        Notice that the variable are accompanied by their respective sizes, not their absolute offset!
        The absolute offset will be calculated internally, so you don't have to worry about it.

        :param ubo_id: str, unique id used in self.ubos
        :param binding_point: int, same number reflected in the GLSL's variable 'binding'. In this example it is 0.
        :param variable_names_and_sizes: list of tuples containing variables in the order they are defined in GLSL
        :return: None
        """

        # Calculate uniform buffer size while taking into account 16bytes memory alignment
        total_size = sum(size for _, size in variable_names_and_sizes)
        buffer_size = total_size if not total_size % 16 else ((total_size // 16) + 1) * 16

        # Calculate offsets for each variable
        offsets = dict(zip(
            (name for name, _ in variable_names_and_sizes),
            accumulate([size for _, size in variable_names_and_sizes], initial=0)
        ))

        # Create the UBO
        ubo = self.ctx.buffer(reserve=buffer_size)

        # Bind the UBO to a binding point
        ubo.bind_to_uniform_block(binding_point)

        # Store the UBO instance
        self.ubos[ubo_id] = UBOInstance(ubo, offsets, binding_point)

        self.logger.debug(f"UBO Registered: '{ubo_id}' @ binding{binding_point} | {offsets}")

    def update_ubo(self, ubo_id: str, variable_id: str, data: bytes) -> None:
        """
        Update the UBO with new data.

        :param ubo_id: str, unique id used in self.ubos
        :param variable_id: str, the id of the variable to update
        :param data: bytes, the data to upload for the variable
        :return: None
        """
        if ubo_id not in self.ubos:
            raise ValueError(f"UBO with id {ubo_id} not registered.")

        ubo_instance = self.ubos[ubo_id]
        ubo_buffer = ubo_instance.ubo
        offsets = ubo_instance.offsets

        if variable_id not in offsets:
            raise ValueError(f"Variable {variable_id} not found in UBO {ubo_id}.")

        offset = offsets[variable_id]
        ubo_buffer.write(data, offset=offset)

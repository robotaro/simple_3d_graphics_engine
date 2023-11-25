import numpy as np
import numpy.random

from src.core import constants
from src.components.component import Component


class DebugMesh(Component):
    _type = constants.COMPONENT_TYPE_MESH

    __slots__ = [
        "vaos",
        "positions",
        "vbo_instanced_positions",
        "mesh_type",
        "num_instances",
        "max_num_instances",
        "sphere_radius",
        "box_size_offset",
        "transform_size",
        "visible",
        "dirty"]

    def __init__(self, parameters, system_owned=False):
        super().__init__(parameters=parameters, system_owned=system_owned)

        self.num_instances = 0

        # RAM Vertex data
        self.positions = None

        # GPU (VRAM) Vertex Data
        self.vaos = {}
        self.vbo_instanced_positions = None

        self.mesh_type = Component.dict2string(input_dict=self.parameters,
                                               key="mesh_type",
                                               default_value="points")

        self.max_num_instances = Component.dict2float(input_dict=self.parameters,
                                                      key="max_num_instances",
                                                      default_value=100)

        self.sphere_radius = Component.dict2float(input_dict=self.parameters,
                                                  key="sphere_radius",
                                                  default_value=0.005)

        self.box_size_offset = Component.dict2float(input_dict=self.parameters,
                                                    key="box_size_offset",
                                                    default_value=0.0)

        self.transform_size = Component.dict2float(input_dict=self.parameters,
                                                   key="transform_size",
                                                   default_value=0.1)

        self.visible = Component.dict2bool(input_dict=self.parameters,
                                           key="visible",
                                           default_value=True)

        self.dirty = True

    def initialise(self, **kwargs):

        if self.initialised:
            return

        ctx = kwargs["ctx"]
        shader_library = kwargs["shader_library"]
        vbo_declaration_list = []

        # Allocate memory for debug data
        self.positions = np.zeros((self.max_num_instances, 3), dtype=np.float32)

        # Create VBOs
        self.vbo_instanced_positions = ctx.buffer(reserve=16 * 4 * self.max_num_instances)
        vbo_declaration_list.append((self.vbo_instanced_positions, "f16/i", constants.SHADER_INPUT_VERTEX))

        # Create VAOs
        program = shader_library[constants.SHADER_PROGRAM_DEBUG_FORWARD_PASS]
        self.vaos[constants.SHADER_PROGRAM_DEBUG_FORWARD_PASS] = ctx.vertex_array(program, vbo_declaration_list)

        # DEBUG
        self.num_instances = 10
        self.vbo_instanced_positions.write(numpy.random.rand((self.max_num_instances, 16)).astype('f4'))

        self.initialised = True

    def upload_buffers(self) -> None:

        # Not being used yet

        if not self.dirty or not self.initialised:
            return

        if self.num_instances > 0:
            self.vbo_intanced_positions.write(self.positions[:, self.num_instances].tobytes())

    def update_new_number_of_elements(self, num_elements: int):
        """
        Call this function every time you finish modifying the vertex data. It will ensure that the
        next render cycle will upload the right number of elements to the GPU
        :param num_elements:
        :return:
        """
        self.num_instances = num_elements
        self.dirty = True

    def render(self, shader_pass_name: str):
        if self.num_instances == 0:
            return

        self.vaos[shader_pass_name].render(vertices=-1, instances=self.num_instances)

    def release(self):

        for _, vao in self.vaos:
            vao.release()

        if self.vbo_intanced_positions:
            self.vbo_intanced_positions.release()



import moderngl
import numpy as np
import trimesh

from core.mesh import Mesh
from core.viewport import Viewport
from core.shader_library import ShaderLibrary
from core.camera import Camera, PerspectiveCamera, OrthographicCamera
from core.light import DirectionalLight
from core.node import Node
from core.utilities import utils_colors


class Scene:

    __slots__ = [
        "name",
        "uid_counter",
        "_meshes",
        "_directional_lights",
        "_cameras",
        "_root_node",
        "_background_color",
        "_ambient_light_color"
    ]

    def __init__(self,
                 name: str,
                 background_color=(1.0, 1.0, 1.0),
                 ambient_light_color=(1.0, 1.0, 1.0)):

        self.name = name
        self.uid_counter = 0

        # Internal Nodes
        self._meshes = []
        self._directional_lights = []
        self._cameras = []

        # Nodes
        self._root_node = Node(name="root_node")

        # Lighting
        self._background_color = background_color
        self._ambient_light_color = ambient_light_color

        # Flags


    # =========================================================================
    #                         Create functions
    # =========================================================================

    def create_directional_light(self,
                                 name: str,
                                 direction=(-1.0, -1.0, -1.0),
                                 color=(1.0, 1.0, 1.0),
                                 intensity=0.5) -> DirectionalLight:

        new_light = DirectionalLight(name=name,
                                     color=color,
                                     intensity=intensity,
                                     direction=direction)

        self._directional_lights.append(new_light)

        return new_light

    def create_perspective_camera(self,
                                  name: str,
                                  position=(5, 5, 5),
                                  aspect_ratio=800/600,
                                  target=(0, 0, 0),
                                  y_pov_deg=45.0) -> PerspectiveCamera:

        new_camera = PerspectiveCamera(name=name, y_fov_deg=y_pov_deg, position=position, aspect_ratio=aspect_ratio)

        self._cameras.append(new_camera)

        return new_camera

    # =========================================================================
    #                           Rendering Functions
    # =========================================================================

    def render_forward_pass(self, context: moderngl.Context, shader_library: ShaderLibrary, viewport: Viewport):

        # REMEMBER THIS:  Scene rendering is during the FORWARD PASS!

        light_nodes = []
        self._root_node.get_nodes_by_type(_type="directional_light", output_list=light_nodes)

        meshes = []
        self._root_node.get_nodes_by_type(_type="mesh", output_list=meshes)

        # [ Stage : Forward Pass ]
        for mesh in meshes:

            # TODO: Skip mesh if invisible

            program = shader_library.get_program(mesh.forward_pass_program_name)

            # Set camera uniforms
            self.upload_camera_uniforms(program=program,
                                        camera=viewport.camera,
                                        viewport_width=viewport.width,
                                        viewport_height=viewport.height)

            # Set light uniforms
            #program["ambient_strength"] = self._ambient_light_color

            # Se model uniforms
            mesh.render_forward_pass(program=program)

        # Stage: Draw transparent objects back to front

        # TODO: Group renderables per program and render them all in batches to minimise program switching
        #

    def upload_camera_uniforms(self,
                               program: moderngl.Program,
                               camera: Camera,
                               viewport_width: float,
                               viewport_height: float):

        proj_matrix_bytes = camera.get_projection_matrix(width=viewport_width, height=viewport_height).T.astype('f4').tobytes()
        program["projection_matrix"].write(proj_matrix_bytes)

        view_matrix_bytes = camera.get_view_matrix().T.astype('f4').tobytes()
        program["view_matrix"].write(view_matrix_bytes)



    def clear(self):
        """Clear out all nodes to form an empty scene.
        """
        self._root_node = Node()

        self._name_to_nodes = {}
        self._obj_to_nodes = {}
        self._obj_name_to_nodes = {}
        self._meshes = set()
        self._point_light_nodes = set()
        self._spot_light_nodes = set()
        self._directional_lights = set()
        self._cameras = set()
        self._main_camera_node = None

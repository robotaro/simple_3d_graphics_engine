import moderngl
from PIL import Image
import numpy as np
from typing import List, Tuple
from array import array

from core import constants
from core.window import Window
from core.shader_library import ShaderLibrary
from core.scene import Scene
from core.scene import Camera
from core.viewport import Viewport
from core.utilities import utils_logging
from core.geometry_3d import ready_to_render


class Renderer:

    # TODO: Use slots!

    def __init__(self, window: Window, shader_library: ShaderLibrary):

        self.window = window
        self.shader_library = shader_library

        self.framebuffers = {}
        self.textures = {}
        self.samplers = {}
        self.quads = {}

        # Create Framebuffers
        self.texture_offscreen_picking_depth = None
        self.texture_offscreen_picking_viewpos = None
        self.texture_offscreen_picking_tri_id = None
        self.framebuffer_offscreen_picking = None

        self.outline_texture = None
        self.outline_framebuffer = None

        # Debug offscreen rendering
        self.offscreen_framebuffer = None
        self.offscreen_diffuse = None
        self.offscreen_normals = None
        self.offscreen_depth = None

        self.create_framebuffers()

        # Create programs
        self.shadow_map_program = None
        self.fragment_picker_program = None

        # Debugging variables
        self.quad_debug = ready_to_render.quad_2d(context=window.context, shader_library=self.shader_library)

        self.logger = utils_logging.get_project_logger()

    def initialize(self):

        self.textures["offscreen_diffuse"] = self.window.context.texture(self.window.buffer_size, 4)
        self.textures["offscreen_normals"] = self.window.context.texture(self.window.buffer_size, 4, dtype='f2')
        self.textures["offscreen_viewpos"] = self.window.context.texture(self.window.buffer_size, 4, dtype='f4')
        self.textures["offscreen_depth"] = self.window.context.depth_texture(self.window.buffer_size)

        self.framebuffers["offscreen"] = self.window.context.framebuffer(
            color_attachments=[
                self.textures["offscreen_diffuse"],
                self.textures["offscreen_normals"],
                self.textures["offscreen_viewpos"],
            ],
            depth_attachment=self.textures["offscreen_depth"],
        )

        self.samplers["depth_sampler"] = self.window.context.sampler(
            filter=(moderngl.LINEAR, moderngl.LINEAR),
            compare_func='',
        )

        # Shaders
        self.shader_library["texture"]["texture0"].value = 0
        self.shader_library["mesh_offscreen"]["texture0"].value = 0

        # Quads
        self.quads["normals"] = ready_to_render.quad_2d(context=self.window.context,
                                                        size=(0.25, 0.25),
                                                        position=(0.75, 0.875),
                                                        shader_library=self.shader_library)
        self.quads["fullscreen"] = ready_to_render.quad_2d(context=self.window.context,
                                                           shader_library=self.shader_library)


        # DEBUG
        self.program = self.window.context.program(
            vertex_shader="""
                            #version 330

                            in vec2 in_position;
                            in vec2 in_uv;
                            out vec2 uv;

                            void main() {
                                gl_Position = vec4(in_position, 0.0, 1.0);
                                uv = in_uv;
                            }
                        """,
            fragment_shader="""
                            #version 330

                            uniform sampler2D image;
                            in vec2 uv;
                            out vec4 out_color;

                            void main() {
                                // Get the Red, green, blue values from the image
                                float red = texture(image, uv).r;
                                // Offset green and blue
                                float green = texture(image, uv+(1.0/20.0)).g;
                                float blue = texture(image, uv+(2.0/20.0)).b;
                                float alpha = texture(image, uv).a;

                                out_color = vec4(red, green, blue, alpha);
                            }
                        """,
        )

        self.vertices = self.window.context.buffer(
            array(
                'f',
                [
                    # Triangle strip creating a fullscreen quad
                    # x, y, u, v
                    -1, 1, 0, 1,  # upper left
                    -1, -1, 0, 0,  # lower left
                    1, 1, 1, 1,  # upper right
                    1, -1, 1, 0,  # lower right
                ]
            )
        )
        self.quad = self.window.context.vertex_array(
            self.program,
            [
                (self.vertices, '2f 2f', 'in_position', 'in_uv'),
            ]
        )

    def create_framebuffers(self):

        # Release framebuffers if they already exist.
        def safe_release(buffer):
            if buffer is not None:
                buffer.release()

        safe_release(self.texture_offscreen_picking_depth)
        safe_release(self.texture_offscreen_picking_viewpos)
        safe_release(self.texture_offscreen_picking_tri_id)
        safe_release(self.framebuffer_offscreen_picking)
        safe_release(self.outline_texture)
        safe_release(self.outline_framebuffer)

        # Mesh mouse intersection
        self.texture_offscreen_picking_depth = self.window.context.depth_texture(self.window.buffer_size)
        self.texture_offscreen_picking_viewpos = self.window.context.texture(self.window.buffer_size, 4, dtype="f4")
        self.texture_offscreen_picking_tri_id = self.window.context.texture(self.window.buffer_size, 4, dtype="f4")
        self.framebuffer_offscreen_picking = self.window.context.framebuffer(
            color_attachments=[self.texture_offscreen_picking_viewpos, self.texture_offscreen_picking_tri_id],
            depth_attachment=self.texture_offscreen_picking_depth,
        )
        self.texture_offscreen_picking_tri_id.filter = (moderngl.NEAREST, moderngl.NEAREST)

        # Outline rendering
        self.outline_texture = self.window.context.texture(self.window.buffer_size, 1, dtype="f4")
        self.outline_framebuffer = self.window.context.framebuffer(color_attachments=[self.outline_texture])

    def load_texture_from_file(self, texture_fpath: str, texture_id: str, datatype="f4"):
        if texture_id in self.textures:
            raise KeyError(f"[ERROR] Texture ID '{texture_id}' already exists")

        image = Image.open(texture_fpath)
        image_data = np.array(image)
        self.textures[texture_id] = self.window.context.texture(size=image.size,
                                                                components=image_data.shape[-1],
                                                                data=image_data.tobytes())

    # =========================================================================
    #                         Render functions
    # =========================================================================

    def render(self, scene: Scene, viewports: List[Viewport]):

        # TODO: Add a substage that checks if a node has a program already defined, and not,
        #       assing a program to it based on its type, otherwise, leave the default program

        # Stage: Render shadow maps

        # Stage: For each viewport render viewport
        #   - Render fragment map picking
        #   - Render scene
        #   - Render outline

        # Initialise object on the GPU if they haven't been already
        scene._root_node.make_renderable(mlg_context=self.window.context,
                                         shader_library=self.shader_library)

        self.render_shadowmap(scene=scene)

        for viewport in viewports:

            self.demo_pass(viewport=viewport)

            #self.offscreen_and_onscreen_pass(scene=scene, viewport=viewport)

            #self.fragment_map_pass(scene=scene, viewport=viewport)
            #self.forward_pass(scene=scene, viewport=viewport)
            #self.outline_pass(scene=scene, viewport=viewport)

    def demo_pass(self, viewport: Viewport):

        if "ball" not in self.textures:
            return

        self.window.context.screen.use()

        self.textures["ball"].use(0)
        #self.quad.render(mode=moderngl.TRIANGLE_STRIP)
        self.quads["fullscreen"]["vao"].render(mode=moderngl.TRIANGLES)

    def offscreen_and_onscreen_pass(self, scene: Scene, viewport: Viewport):

        self.window.context.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

        # =================[ Offscreen Rendering ]=====================
        self.framebuffers["offscreen"].clear()
        self.framebuffers["offscreen"].use()

        mesh_program = self.shader_library["mesh_offscreen"]

        self.upload_camera_uniforms(program=mesh_program, viewport=viewport)

        self.samplers["depth_sampler"].use(location=0)
        meshes = scene.get_nodes_by_type(node_type="mesh")
        for mesh in meshes:

            if mesh._vbo_dirty_flag:
                mesh.upload_buffers()
                mesh._vbo_dirty_flag = False

            # Upload uniforms
            mesh_program["model_matrix"].write(mesh.transform.T.astype('f4').tobytes())
            mesh.vao.render()

        self.samplers["depth_sampler"].clear(location=0)

        self.window.context.screen.use()
        self.window.context.disable(moderngl.DEPTH_TEST)

        self.textures["offscreen_color"].use(location=0)
        self.quads["fullscreen"]["vao"].render()

    def forward_pass(self, scene: Scene, viewport: Viewport):

        # IMPORTANT: You MUST have called scene.make_renderable once before getting here!

        # Bind screen context to draw to it
        self.window.context.screen.use()

        # TODO: maybe move this to inside the scene?
        # Clear context (you need to use the use() first to bind it!)
        self.window.context.clear(
            red=scene._background_color[0],
            green=scene._background_color[1],
            blue=scene._background_color[2],
            alpha=0.0,
            depth=1.0,
            viewport=viewport.to_tuple())

        # Prepare context flags for rendering
        self.window.context.enable_only(moderngl.DEPTH_TEST | moderngl.BLEND | moderngl.CULL_FACE)
        self.window.context.cull_face = "back"
        self.window.context.blend_func = (
            moderngl.SRC_ALPHA,
            moderngl.ONE_MINUS_SRC_ALPHA,
            moderngl.ONE,
            moderngl.ONE)

        # Render scene
        light_nodes = scene.get_nodes_by_type(node_type="directional_light")
        meshes = scene.get_nodes_by_type(node_type="mesh")

        # [ Stage : Forward Pass ]
        for mesh in meshes:
            # TODO: Skip mesh if invisible

            program = self.shader_library[mesh.forward_pass_program_name]

            # Set camera uniforms
            self.upload_camera_uniforms(program=program, viewport=viewport)

            # Set light uniforms
            # program["ambient_strength"] = self._ambient_light_color

            # Upload buffers ONLY if necessary
            if mesh._vbo_dirty_flag:
                mesh.upload_buffers()
                mesh._vbo_dirty_flag = False

            # Upload uniforms
            program["model_matrix"].write(mesh.transform.T.astype('f4').tobytes())

            # Render the vao at the end
            mesh.vao.render(moderngl.TRIANGLES)

        # Stage: Draw transparent objects back to front

    def fragment_map_pass(self, scene: Scene, viewport: Viewport):
        self.window.context.enable_only(moderngl.DEPTH_TEST)
        self.framebuffer_offscreen_picking.use()
        self.framebuffer_offscreen_picking.viewport = viewport.to_tuple()

        meshes = []
        scene._root_node.get_nodes_by_type(node_type="mesh", output_list=meshes)

        # Same fragment picking program for all meshes
        program = self.shader_library["fragment_picking"]

        # [ Stage : Fragment Picking Pass ]
        for mesh in meshes:
            # Set camera uniforms
            self.upload_camera_uniforms(program=program, viewport=viewport)

            # Render with the specified object uid, if None use the node uid instead.
            program["object_id"] = mesh.uid

            # if self.backface_culling or self.backface_fragmap:
            self.window.context.enable(moderngl.CULL_FACE)
            # else:
            #    context.disable(moderngl.CULL_FACE)

            # If backface_fragmap is enabled for this node only render backfaces
            # if self.backface_fragmap:
            #    context.cull_face = "front"

            # Restore cull face to back
            # if self.backface_fragmap:
            #    context.cull_face = "back"

    def outline_pass(self, scene: Scene, viewport: Viewport):
        #print("[Renderer] _outline_pass")
        pass


    def render_shadowmap(self, scene: Scene):

        #print("[Renderer] render_shadowmap")

        """if bool(flags & constants.RENDER_FLAG_DEPTH_ONLY or flags & constants.RENDER_FLAG_SEG):
            return

        for ln in scene.light_nodes:
            take_pass = False
            if (isinstance(ln.light, DirectionalLight) and
                    bool(flags & RenderFlags.SHADOWS_DIRECTIONAL)):
                take_pass = True
            elif (isinstance(ln.light, SpotLight) and
                  bool(flags & RenderFlags.SHADOWS_SPOT)):
                take_pass = True
            elif (isinstance(ln.light, PointLight) and
                  bool(flags & RenderFlags.SHADOWS_POINT)):
                take_pass = True
            if take_pass:
                self.render_pass_shadow_mapping(scene, ln, flags)"""
        pass


    @staticmethod
    def upload_camera_uniforms(program: moderngl.Program,
                               viewport: Viewport):
        proj_matrix_bytes = viewport.camera.get_projection_matrix(
            width=viewport.width,
            height=viewport.height).T.astype('f4').tobytes()
        program["projection_matrix"].write(proj_matrix_bytes)

        view_matrix_bytes = viewport.camera.get_view_matrix().T.astype('f4').tobytes()
        program["view_matrix"].write(view_matrix_bytes)


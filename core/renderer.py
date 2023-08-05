import moderngl
import numpy as np
from typing import List, Tuple

from core import constants
from core.window import Window
from core.shader_library import ShaderLibrary
from core.scene import Scene
from core.scene import Camera
from core.viewport import Viewport
from core.utilities import utils_logging


class Renderer:

    # TODO: Use slots!

    def __init__(self, window: Window, shader_library: ShaderLibrary):

        self.window = window
        self.shader_library = shader_library

        # Create Framebuffers
        self.texture_offscreen_picking_depth = None
        self.texture_offscreen_picking_viewpos = None
        self.texture_offscreen_picking_tri_id = None
        self.framebuffer_offscreen_picking = None
        self.outline_texture = None
        self.outline_framebuffer = None
        self.create_framebuffers()

        # Create programs
        self.shadow_map_program = None
        self.fragment_picker_program = None

        self.logger = utils_logging.get_project_logger()

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
            self.fragment_map_pass(scene=scene, viewport=viewport)
            self.forward_pass(scene=scene, viewport=viewport)
            self.outline_pass(scene=scene, viewport=viewport)

    def set_camera_matrices(self, prog, camera, **kwargs):
        """Set the model view projection matrix in the given program."""
        # Transpose because np is row-major but OpenGL expects column-major.
        prog["model_matrix"].write(self.model_matrix.T.astype("f4").tobytes())
        prog["view_projection_matrix"].write(camera.get_view_projection_matrix().T.astype("f4").tobytes())

    # =========================================================================
    #                        Framebuffer functions
    # =========================================================================

    def create_framebuffers(self):

        # Release framebuffers if they already exist.
        def safe_release(b):
            if b is not None:
                b.release()

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

    # =========================================================================
    #                         Render Pass functions
    # =========================================================================

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
        scene.render_forward_pass(context=self.window.context,
                                  shader_library=self.shader_library,
                                  viewport=viewport)

    def fragment_map_pass(self, scene: Scene, viewport: Viewport):
        self.window.context.enable_only(moderngl.DEPTH_TEST)
        self.framebuffer_offscreen_picking.use()
        self.framebuffer_offscreen_picking.viewport = viewport.to_tuple()

        scene.render_fragment_picking_pass(context=self.window.context,
                                           shader_library=self.shader_library,
                                           viewport=viewport)

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


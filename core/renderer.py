import moderngl
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
        self.offscreen_texture_depth = None
        self.offscreen_texture_viewpos = None
        self.offscreen_texture_tri_id = None
        self.offscreen_framebuffer = None
        self.outline_texture = None
        self.outline_framebuffer = None
        #self.headless_fbo_color = None
        #self.headless_fbo_depth = None
        #self.headless_fbo = None
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
        self._update_context(scene=scene)

        self.render_shadowmap(scene=scene)

        for viewport in viewports:

            self._fragment_map_pass(scene=scene, viewport=viewport)
            self._forward_pass(scene=scene, viewport=viewport)
            self._outline_pass(scene=scene, viewport=viewport)


    def _update_context(self, scene: Scene):

        #print("[Renderer] _update_context")

        # Setup lights here
        scene.root_node.make_renderable(mlg_context=self.window.context,
                                        all_programs=self.shader_library.programs)


        # Update mesh textures
        """mesh_textures = set()
        for m in scene_meshes:
            for p in m.primitives:
                mesh_textures |= p.material.textures

        # Add new textures to context
        for texture in mesh_textures - self._mesh_textures:
            texture._add_to_context()

        # Remove old textures from context
        for texture in self._mesh_textures - mesh_textures:
            texture.delete()

        self._mesh_textures = mesh_textures.copy()

        shadow_textures = set()
        for l in scene.lights:
            # Create if needed
            active = False
            if (isinstance(l, DirectionalLight) and
                    flags & RenderFlags.SHADOWS_DIRECTIONAL):
                active = True
            elif (isinstance(l, PointLight) and
                    flags & RenderFlags.SHADOWS_POINT):
                active = True
            elif isinstance(l, SpotLight) and flags & RenderFlags.SHADOWS_SPOT:
                active = True

            if active and l.shadow_texture is None:
                l._generate_shadow_texture()
            if l.shadow_texture is not None:
                shadow_textures.add(l.shadow_texture)

        # Add new textures to context
        for texture in shadow_textures - self._shadow_textures:
            texture._add_to_context()

        # Remove old textures from context
        for texture in self._shadow_textures - shadow_textures:
            texture.delete()

        self._shadow_textures = shadow_textures.copy()"""


    def _use_program(self, camera, **kwargs):

        if self.has_texture and self.show_texture:
            prog = self.texture_prog
            prog["diffuse_texture"] = 0
            self.texture.use(0)
        else:
            if self.face_colors is None:
                if self.flat_shading:
                    prog = self.flat_prog
                else:
                    prog = self.smooth_prog
            else:
                if self.flat_shading:
                    prog = self.flat_face_prog
                else:
                    prog = self.smooth_face_prog
                self.face_colors_texture.use(0)
                prog["face_colors"] = 0
            prog["norm_coloring"].value = self.norm_coloring

        prog["use_uniform_color"] = self._use_uniform_color
        prog["uniform_color"] = self.material.color
        prog["draw_edges"].value = 1.0 if self.draw_edges else 0.0
        prog["win_size"].value = kwargs["window_size"]

        prog["clip_control"].value = tuple(self.clip_control)
        prog["clip_value"].value = tuple(self.clip_value)

        self.set_camera_matrices(prog, camera, **kwargs)
        set_lights_in_program(
            prog,
            kwargs["lights"],
            kwargs["shadows_enabled"],
            kwargs["ambient_strength"],
        )
        set_material_properties(prog, self.material)
        self.receive_shadow(prog, **kwargs)
        return prog

    # =========================================================================
    #                        Framebuffer functions
    # =========================================================================

    def create_framebuffers(self):

        # Release framebuffers if they already exist.
        def safe_release(b):
            if b is not None:
                b.release()

        safe_release(self.offscreen_texture_depth)
        safe_release(self.offscreen_texture_viewpos)
        safe_release(self.offscreen_texture_tri_id)
        safe_release(self.offscreen_framebuffer)
        safe_release(self.outline_texture)
        safe_release(self.outline_framebuffer)

        # Mesh mouse intersection
        self.offscreen_texture_depth = self.window.context.depth_texture(self.window.buffer_size)
        self.offscreen_texture_viewpos = self.window.context.texture(self.window.buffer_size, 4, dtype="f4")
        self.offscreen_texture_tri_id = self.window.context.texture(self.window.buffer_size, 4, dtype="f4")
        self.offscreen_framebuffer = self.window.context.framebuffer(
            color_attachments=[self.offscreen_texture_viewpos, self.offscreen_texture_tri_id],
            depth_attachment=self.offscreen_texture_depth,
        )
        self.offscreen_texture_tri_id.filter = (moderngl.NEAREST, moderngl.NEAREST)

        # Outline rendering
        self.outline_texture = self.window.context.texture(self.window.buffer_size, 1, dtype="f4")
        self.outline_framebuffer = self.window.context.framebuffer(color_attachments=[self.outline_texture])

        # If in headlesss mode we create a framebuffer without multisampling that we can use
        # to resolve the default framebuffer before reading.
        #if self.window_type == "headless":
        #    safe_release(self.headless_fbo_color)
        #    safe_release(self.headless_fbo_depth)
        #    safe_release(self.headless_fbo)
        #    self.headless_fbo_color = self.ctx.texture(self.wnd.buffer_size, 4)
        #    self.headless_fbo_depth = self.ctx.depth_texture(self.wnd.buffer_size)
        #    self.headless_fbo = self.ctx.framebuffer(self.headless_fbo_color, self.headless_fbo_depth)

    # =========================================================================
    #                         Render Pass functions
    # =========================================================================

    def _forward_pass(self, scene: Scene, viewport: Viewport):

        #print("[Renderer] _forward_pass")

        # Bind screen context to draw to it
        self.window.context.screen.use()

        # TODO: maybe move this to inside the scene?
        # Clear context (you need to use the use() first to bind it!)
        self.window.context.clear(
            red=scene.bg_color[0],
            green=scene.bg_color[1],
            blue=scene.bg_color[2],
            alpha=0.0,
            depth=1.0,
            viewport=viewport.get_tuple())

        # Set up viewport for render
        self.configure_forward_pass_context(context=self.window.context)

        scene.root_node.make_renderable(mlg_context=self.window.context,
                                        all_programs=self.shader_library.programs)

        scene.root_node.render(viewport=viewport)

        # Clear contexts
        """if bool(flags & RenderFlags.SEG):
            glClearColor(0.0, 0.0, 0.0, 1.0)
            if seg_node_map is None:
                seg_node_map = {}
        else:
            glClearColor(*scene.bg_color)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if not bool(flags & RenderFlags.SEG):
            glEnable(GL_MULTISAMPLE)
        else:
            glDisable(GL_MULTISAMPLE)

        # Set up camera matrices
        V, P = self._get_camera_matrices(scene)

        program = None
        # Now, render each object in sorted order
        for node in self._sorted_mesh_nodes(scene):
            mesh = node.mesh

            # Skip the mesh if it's not visible
            if not mesh.is_visible:
                continue

            # If SEG, set color
            if bool(flags & RenderFlags.SEG):
                if node not in seg_node_map:
                    continue
                color = seg_node_map[node]
                if not isinstance(color, (list, tuple, np.ndarray)):
                    color = np.repeat(color, 3)
                else:
                    color = np.asanyarray(color)
                color = color / 255.0

            for primitive in mesh.primitives:

                # First, get and bind the appropriate program
                program = self._get_primitive_program(
                    primitive, flags, ProgramFlags.USE_MATERIAL
                )
                program._bind()

                # Set the camera uniforms
                program.set_uniform('V', V)
                program.set_uniform('P', P)
                program.set_uniform(
                    'cam_pos', scene.get_pose(scene.main_camera_node)[:3,3]
                )
                if bool(flags & RenderFlags.SEG):
                    program.set_uniform('color', color)

                # Next, bind the lighting
                if not (flags & RenderFlags.DEPTH_ONLY or flags & RenderFlags.FLAT or
                        flags & RenderFlags.SEG):
                    self._bind_lighting(scene, program, node, flags)

                # Finally, bind and draw the primitive
                self._bind_and_draw_primitive(
                    primitive=primitive,
                    pose=scene.get_pose(node),
                    program=program,
                    flags=flags
                )
                self._reset_active_textures()

        # Unbind the shader and flush the output
        if program is not None:
            program._unbind()
        glFlush()

        # If doing offscreen render, copy result from framebuffer and return
        if flags & RenderFlags.OFFSCREEN:
            return self._read_main_framebuffer(scene, flags)
        else:
            return"""

    def _fragment_map_pass(self, scene: Scene, viewport: Viewport):
        print("[Renderer] _fragment_map_pass")
        pass

    def _outline_pass(self, scene: Scene, viewport: Viewport):
        print("[Renderer] _outline_pass")
        pass


    def render_shadowmap(self, scene: Scene):

        print("[Renderer] render_shadowmap")

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

    # =========================================================================
    #                         Context configuring funcitons
    # =========================================================================

    def configure_forward_pass_context(self, context: moderngl.Context) -> None:
        print("[Renderer] configure_forward_pass_context")
        context.enable_only(moderngl.DEPTH_TEST | moderngl.BLEND | moderngl.CULL_FACE)
        context.cull_face = "back"
        context.blend_func = (
            moderngl.SRC_ALPHA,
            moderngl.ONE_MINUS_SRC_ALPHA,
            moderngl.ONE,
            moderngl.ONE,
        )

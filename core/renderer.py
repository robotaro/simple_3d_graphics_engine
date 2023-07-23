import moderngl

from core import constants
from core.window import Window
from core.shader_library import ShaderLibrary
from core.scene import Scene
from core.scene import Camera


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
        self.mesh_program = shader_library.get_program(program_id="shader")
        g = 0

    def render(self, scene: Scene, camera: Camera, flags, seg_node_map=None):

        # Initialise object on the GPU if they haven't been already
        self._update_context(scene, flags)

        # Render necessary shadow maps
        self.render_shadowmap()

        # Make forward pass
        retval = self.render_pass_forward(scene, flags, seg_node_map=seg_node_map)

        # If necessary, make normals pass
        if flags & (constants.RENDER_FLAG_VERTEX_NORMALS | constants.RENDER_FLAG_FACE_NORMALS):
            self._normals_pass(scene, flags)

        # Update camera settings for retrieving depth buffers
        self._latest_znear = camera.z_near
        self._latest_zfar = camera.z_far

        return retval

    def _update_context(self, scene: Scene, flags: list):

        scene.root_node.make_renderable()

        # Update mesh textures
        mesh_textures = set()
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

        self._shadow_textures = shadow_textures.copy()

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
    #                      Rendering functions
    # =========================================================================

    def render_shadowmap(self, scene: Scene, flags: int):

        if bool(flags & constants.RENDER_FLAG_DEPTH_ONLY or flags & constants.RENDER_FLAG_SEG):
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
                self.render_pass_shadow_mapping(scene, ln, flags)

    def render_outline(self):
        pass

    def renderpass_outline(self):
        pass
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
        self.offscreen_p_depth = None
        self.offscreen_p_viewpos = None
        self.offscreen_p_tri_id = None
        self.offscreen_p = None
        self.outline_texture = None
        self.outline_framebuffer = None
        self.headless_fbo_color = None
        self.headless_fbo_depth = None
        self.headless_fbo = None
        self.create_framebuffers()

    def render(self, scene: Scene, camera: Camera, flags, seg_node_map=None):

        # Update context with meshes and textures
        self._update_context(scene, flags)

        # Render necessary shadow maps
        self.render_shadowmap()

        # Make forward pass
        retval = self.render_pass_forward(scene, flags, seg_node_map=seg_node_map)

        # If necessary, make normals pass
        if flags & (constants.RENDER_FLAG_VERTEX_NORMALS | constants.RENDER_FLAG_FACE_NORMALS):
            self._normals_pass(scene, flags)

        # Update camera settings for retrieving depth buffers
        self._latest_znear = scene.main_camera_node.camera.znear
        self._latest_zfar = scene.main_camera_node.camera.zfar

        return retval

    # =========================================================================
    #                      Framebuffer functions
    # =========================================================================

    def create_framebuffers(self):

        pass

    # =========================================================================
    #                      Rendering functions
    # =========================================================================

    def render(self, scene: Scene, camera):


        # Forward pass

        # Shadow pass
        pass

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
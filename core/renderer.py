from core.window import Window
from core.shader_library import ShaderLibrary


class Renderer:

    def __init__(self, window: Window, shader_library: ShaderLibrary):

        self.window = window
        self.shader_library = shader_library

        # Shaders for mesh mouse intersection.
        """self.frag_pick_prog = load_program("fragment_picking/frag_pick.glsl")
        self.frag_pick_prog["position_texture"].value = 0  # Read from texture channel 0
        self.frag_pick_prog["obj_info_texture"].value = 1  # Read from texture channel 0
        self.picker_output = self.ctx.buffer(reserve=6 * 4)  # 3 floats, 3 ints
        self.picker_vao = VAO(mode=moderngl.POINTS)

        # Shaders for drawing outlines.
        self.outline_draw_prog = load_program("outline/outline_draw.glsl")
        self.outline_quad = geometry.quad_2d(size=(2.0, 2.0), pos=(0.0, 0.0))

        # Create framebuffers
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

        # Debug
        self.vis_prog = load_program("visualize.glsl")
        self.vis_quad = geometry.quad_2d(size=(0.9, 0.9), pos=(0.5, 0.5))"""


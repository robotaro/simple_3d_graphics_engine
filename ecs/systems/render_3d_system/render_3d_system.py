import moderngl
from PIL import Image
import numpy as np
from typing import Tuple
import struct

from ecs import constants
from ecs.systems.system import System
from ecs.shader_library import ShaderLibrary
from ecs.component_pool import ComponentPool
from core.geometry_3d import ready_to_render


class Render3DSystem(System):

    _type = "render_3d_system"

    def __init__(self, **kwargs):
        super().__init__(logger=kwargs["logger"])

        self.ctx = kwargs["context"]
        self.buffer_size = kwargs["buffer_size"]
        self.shader_library = ShaderLibrary(context=self.ctx)

        # Internal components (different from normal components)
        self.framebuffers = {}
        self.textures = {}
        self.samplers = {}
        self.vbo_groups = {}
        self.quads = {}

        # Fragment Picking - altogether for now
        self.fragment_picker_program = None
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

        # Create programs
        self.shadow_map_program = None

        # Debugging variables
        self.quad_debug = None

    # =========================================================================
    #                         System Core functions
    # =========================================================================

    def initialise(self, **kwargs):

        # Get data from arguments
        self.safe_release(self.texture_offscreen_picking_depth)
        self.safe_release(self.texture_offscreen_picking_viewpos)
        self.safe_release(self.texture_offscreen_picking_tri_id)
        self.safe_release(self.framebuffer_offscreen_picking)
        self.safe_release(self.outline_texture)
        self.safe_release(self.outline_framebuffer)

        # Mesh mouse intersection
        self.texture_offscreen_picking_depth = self.ctx.depth_texture(self.buffer_size)
        self.texture_offscreen_picking_viewpos = self.ctx.texture(self.buffer_size, 4, dtype="f4")
        self.texture_offscreen_picking_tri_id = self.ctx.texture(self.buffer_size, 4, dtype="f4")
        self.framebuffer_offscreen_picking = self.ctx.framebuffer(
            color_attachments=[self.texture_offscreen_picking_viewpos, self.texture_offscreen_picking_tri_id],
            depth_attachment=self.texture_offscreen_picking_depth,
        )
        self.texture_offscreen_picking_tri_id.filter = (moderngl.NEAREST, moderngl.NEAREST)

        # Outline rendering
        self.outline_texture = self.ctx.texture(self.buffer_size, 1, dtype="f4")
        self.outline_framebuffer = self.ctx.framebuffer(color_attachments=[self.outline_texture])

        self.textures["offscreen_diffuse"] = self.ctx.texture(self.buffer_size, 4)
        self.textures["offscreen_normals"] = self.ctx.texture(self.buffer_size, 4, dtype='f2')
        self.textures["offscreen_viewpos"] = self.ctx.texture(self.buffer_size, 4, dtype='f4')
        self.textures["offscreen_depth"] = self.ctx.depth_texture(self.buffer_size)

        self.framebuffers["offscreen"] = self.ctx.framebuffer(
            color_attachments=[
                self.textures["offscreen_diffuse"],
                self.textures["offscreen_normals"],
                self.textures["offscreen_viewpos"],
            ],
            depth_attachment=self.textures["offscreen_depth"],
        )

        self.samplers["depth_sampler"] = self.ctx.sampler(
            filter=(moderngl.LINEAR, moderngl.LINEAR),
            compare_func='',
        )

        # Shaders
        self.shader_library["texture"]["texture0"].value = 0
        self.shader_library["mesh_offscreen"]["texture0"].value = 0

        # Quads
        self.quad_debug = ready_to_render.quad_2d(context=self.ctx, shader_library=self.shader_library)
        self.quads["normals"] = ready_to_render.quad_2d(context=self.ctx,
                                                        size=(0.25, 0.25),
                                                        position=(0.75, 0.875),
                                                        shader_library=self.shader_library)
        self.quads["fullscreen"] = ready_to_render.quad_2d(context=self.ctx,
                                                           shader_library=self.shader_library)

        return True

    def update(self,
               elapsed_time: float,
               component_pool: ComponentPool,
               context: moderngl.Context,
               event=None):

        # Initialise object on the GPU if they haven't been already

        for entity_uid, renderable in component_pool.renderable_components.items():

            mesh = component_pool.mesh_components[entity_uid]
            mesh.initialise_on_gpu(ctx=self.ctx)
            renderable.initialise_on_gpu(ctx=self.ctx,
                                         program_name_list=[constants.RENDER_SYSTEM_PROGRAM_FORWARD_PASS],
                                         shader_library=self.shader_library,
                                         vbo_tuple_list=mesh.get_vbo_declaration_list(),
                                         ibo_faces=mesh.ibo_faces)

        # Renderable entity IDs
        renderable_entity_uids = list(component_pool.renderable_components.keys())
        camera_entity_uids = list(component_pool.camera_components.keys())

        for camera_uid in camera_entity_uids:

            # self.demo_pass(viewport=viewport)

            # self.offscreen_and_onscreen_pass(scene=scene, viewport=viewport)

            self.fragment_map_pass(component_pool=component_pool,
                                   camera_uid=camera_uid,
                                   renderable_uids=renderable_entity_uids)
            self.forward_pass(component_pool=component_pool,
                              camera_uid=camera_uid,
                              renderable_uids=renderable_entity_uids)

            # self.outline_pass(scene=scene, viewport=viewport)


        pass

    def on_event(self, event_type: int, event_data: tuple):

        if event_type == constants.EVENT_MOUSE_BUTTON_PRESS:
            # Get fragment here?
            point_world, obj_id, tri_id, instance_id = self.read_fragmap_at_pixel(x=event_data[0], y=event_data[1])
            self.logger.info(obj_id)

    def shutdown(self):

        # Release textures
        for texture_name, texture_obj in self.textures.items():
            texture_obj.release()

        # Release Framebuffers
        for frabuffer_name, framebuffer_obj in self.framebuffers.items():
            framebuffer_obj.release()

    # =========================================================================
    #                         Render functions
    # =========================================================================

    def fragment_map_pass(self, component_pool: ComponentPool, camera_uid: int, renderable_uids: list):

        camera_component = component_pool.camera_components[camera_uid]
        camera_transform = component_pool.transform_components[camera_uid]

        self.ctx.enable_only(moderngl.DEPTH_TEST)
        self.framebuffer_offscreen_picking.use()
        self.framebuffer_offscreen_picking.viewport = camera_component.viewport

        program = self.shader_library[constants.RENDER_SYSTEM_PROGRAM_FRAGMENT_PICKING_PASS]

        for renderable_uid in renderable_uids:

            renderable_component = component_pool.renderable_components[renderable_uid]

            if not renderable_component.visible:
                continue

            # Set camera uniforms
            camera_component.upload_uniforms(program=program)

            # Render with the specified object uid, if None use the node uid instead.
            program["object_id"] = renderable_uid

            # if self.backface_culling or self.backface_fragmap:
            self.ctx.enable(moderngl.CULL_FACE)
            # else:
            #    context.disable(moderngl.CULL_FACE)

            # If backface_fragmap is enabled for this node only render backfaces
            # if self.backface_fragmap:
            #    context.cull_face = "front"

            # Restore cull face to back
            # if self.backface_fragmap:
            #    context.cull_face = "back"

            renderable_transform = component_pool.transform_components[renderable_uid]

            # Upload uniforms
            program["view_matrix"].write(camera_transform.local_matrix.T.astype('f4').tobytes())
            program["model_matrix"].write(renderable_transform.local_matrix.T.astype('f4').tobytes())

            # Render the vao at the end
            renderable_component.vaos[constants.RENDER_SYSTEM_PROGRAM_FORWARD_PASS].render(moderngl.TRIANGLES)

    def forward_pass(self, component_pool: ComponentPool, camera_uid: int, renderable_uids: list):

        # IMPORTANT: You MUST have called scene.make_renderable once before getting here!

        # Bind screen context to draw to it
        self.ctx.screen.use()

        camera_component = component_pool.camera_components[camera_uid]
        camera_transform = component_pool.transform_components[camera_uid]

        # TODO: maybe move this to inside the scene?
        # Clear context (you need to use the use() first to bind it!)
        self.ctx.clear(
            red=1,
            green=1,
            blue=1,
            alpha=0.0,
            depth=1.0,
            viewport=camera_component.viewport)

        # Prepare context flags for rendering
        self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.BLEND | moderngl.CULL_FACE)
        self.ctx.cull_face = "back"
        self.ctx.blend_func = (
            moderngl.SRC_ALPHA,
            moderngl.ONE_MINUS_SRC_ALPHA,
            moderngl.ONE,
            moderngl.ONE)

        # Render scene
        #light_nodes = scene.get_nodes_by_type(node_type="directional_light")
        #meshes = scene.get_nodes_by_type(node_type="mesh")

        program = self.shader_library[constants.RENDER_SYSTEM_PROGRAM_FORWARD_PASS]

        for renderable_uid in renderable_uids:

            renderable_component = component_pool.renderable_components[renderable_uid]

            if not renderable_component.visible:
                continue

            # Set camera uniforms
            camera_component.upload_uniforms(program=program)

            # Set light uniforms
            # program["ambient_strength"] = self._ambient_light_color

            # Upload buffers ONLY if necessary
            #if mesh._vbo_dirty_flag:
            #    mesh.upload_buffers()
            #    mesh._vbo_dirty_flag = False

            # TODO: Continue from here, switch to uid to get the transforms

            renderable_transform = component_pool.transform_components[renderable_uid]

            camera_transform.update()

            # Upload uniforms
            program["view_matrix"].write(camera_transform.local_matrix.T.astype('f4').tobytes())
            program["model_matrix"].write(renderable_transform.local_matrix.T.astype('f4').tobytes())

            # Render the vao at the end
            renderable_component.vaos[constants.RENDER_SYSTEM_PROGRAM_FORWARD_PASS].render(moderngl.TRIANGLES)

            # Stage: Draw transparent objects back to front

    # =========================================================================
    #                         Other Functions
    # =========================================================================

    # Release framebuffers if they already exist.
    def safe_release(self, buffer: moderngl.Buffer):
        if buffer is not None:
            buffer.release()

    def load_texture_from_file(self, texture_fpath: str, texture_id: str, datatype="f4"):
        if texture_id in self.textures:
            raise KeyError(f"[ERROR] Texture ID '{texture_id}' already exists")

        image = Image.open(texture_fpath)
        image_data = np.array(image)
        self.textures[texture_id] = self.ctx.texture(size=image.size,
                                                     components=image_data.shape[-1],
                                                     data=image_data.tobytes())

    def read_fragmap_at_pixel(self, x: int, y: int) -> Tuple[np.ndarray, int, int, int]:
        """
        Given an (x,y) screen coordinate, get the intersected object, triangle id, and xyz point in camera space.
        """

        # Fragment picker uses already encoded position/object/triangle in the frag_pos program textures
        self.frag_pick_prog["texel_pos"].value = (x, y)
        self.offscreen_p_viewpos.use(location=0)
        self.offscreen_p_tri_id.use(location=1)

        vao.transform(
            buffer, mode=mode, vertices=vertices, first=first, instances=instances
        )

        self.picker_vao.transform(self.frag_pick_prog, self.picker_output, vertices=1)
        x, y, z, obj_id, tri_id, instance_id = struct.unpack("3f3i", self.picker_output.read())
        return np.array((x, y, z)), obj_id, tri_id, instance_id

    """
    def demo_pass(self, viewport: Viewport):

        if "ball" not in self.textures:
            return

        self.ctx.screen.use()
        self.textures["ball"].use(0)
        self.quads["fullscreen"]["vao"].render(mode=moderngl.TRIANGLES)

    def offscreen_and_onscreen_pass(self, scene: Scene, viewport: Viewport):

        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

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

        self.ctx.screen.use()
        self.ctx.disable(moderngl.DEPTH_TEST)

        self.textures["offscreen_diffuse"].use(location=0)
        self.quads["fullscreen"]["vao"].render()"""

    """

    def outline_pass(self, scene: Scene, viewport: Viewport):
        # print("[Renderer] _outline_pass")
        pass

    def render_shadowmap(self, scene: Scene):

        # print("[Renderer] render_shadowmap")

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
        pass
        """

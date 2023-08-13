
import numpy as np
import trimesh
import moderngl
from core.material import Material

from core.node import Node
from core.shader_library import ShaderLibrary


class Mesh(Node):

    _type = "mesh"

    def __init__(self,
                 vertices=None,
                 normals=None,
                 faces=None,
                 uvs=None,
                 material=None,
                 forward_pass_program_name="mesh",
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Actual data stored here
        self.vertices = vertices    # nd.array (N, 3) <float32>
        self.normals = normals     # nd.array (N, 3) <float32>
        self.faces = faces       # nd.array (N, 3) <int32>
        self.uvs = uvs

        # Materials
        self.alpha = 1.0
        self.material = material

        # Buffer Objects
        self.vbo_vertices = None
        self.vbo_normals = None
        self.ibo_faces = None  # Triangular faces
        self.vaos = {}

        # Custom programs - for special features
        self.forward_pass_program_name = forward_pass_program_name

        # Flags
        self._vbo_dirty_flag = True
        self._instanced = False
        self._renderable = True
        self.visible = True
        self._flat_shading = False

    def release(self):

        for name, vao in self.vaos.items():
            vao.release()

        if self.vbo_vertices:
            self.vbo_vertices.release()

        if self.vbo_normals:
            self.vbo_normals.release()

        if self.ibo_faces:
            self.ibo_faces.release()

    @Node.once
    def make_renderable(self, mlg_context: moderngl.Context, shader_library: ShaderLibrary):

        print(f"[{self._type} | {self.name}] make_renderable")

        # TODO: - Check if I need to upload data here or leave it to uploaded buffers
        #       - Check if I need to set these to dynamic

        vbo_list = []

        # Create VBOs
        if self.vertices is not None:
            self.vbo_vertices = mlg_context.buffer(self.vertices.astype("f4").tobytes())
            vbo_list.append((self.vbo_vertices, "3f", "in_vert"))

        if self.normals is not None:
            self.vbo_normals = mlg_context.buffer(self.normals.astype("f4").tobytes())
            vbo_list.append((self.vbo_normals, "3f", "in_normal"))

        program = shader_library[self.forward_pass_program_name]

        if self.faces is None:
            self.vao = mlg_context.vertex_array(program, vbo_list)
        else:
            self.ibo_faces = mlg_context.buffer(self.faces.astype("i4").tobytes())
            self.vao = mlg_context.vertex_array(program, vbo_list, self.ibo_faces)

        # TODO: Add instance-based code

    def upload_uniforms(self, render_pass_name: str):

        # Get program for this render pass
        program = self.vaos[render_pass_name].program

        # Camera uniforms were previously uploaded here
        program["model_matrix"].write(self.transform.T.astype('f4').tobytes())

        # Upload material uniforms
        #if self.material is not None:
        #    self.program["diffuse_coeff"].value = self.material.diffuse
        #    self.program["ambient_coeff"].value = self.material.ambient

        """if self.has_texture and self.show_texture:
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
        self.set_lights_in_program(
            prog,
            kwargs["lights"],
            kwargs["shadows_enabled"],
            kwargs["ambient_strength"],
        )
        self.set_material_properties(prog, self.material)
        self.receive_shadow(prog, **kwargs)
        return prog"""



    # =========================================================================
    #                         Getters and Setters
    # =========================================================================

    @property
    def is_transparent(self):
        if self.material is None:
            return False
        return self.material.is_transparent()

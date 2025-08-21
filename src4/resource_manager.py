# ecs/resource_manager.py
"""Resource manager for loading and caching GPU resources"""
import moderngl
from typing import Dict, Optional


class ResourceManager:
    """Manages GPU resources like VAOs, textures, and shaders"""

    def __init__(self, ctx: moderngl.Context):
        self.ctx = ctx
        self.vaos: Dict[str, moderngl.VertexArray] = {}
        self.textures: Dict[str, moderngl.Texture] = {}
        self.shaders: Dict[str, moderngl.Program] = {}

    def register_vao(self, name: str, vao: moderngl.VertexArray):
        """Register a vertex array object"""
        self.vaos[name] = vao

    def get_vao(self, name: str) -> Optional[moderngl.VertexArray]:
        """Get a vertex array object by name"""
        return self.vaos.get(name)

    def register_texture(self, name: str, texture: moderngl.Texture):
        """Register a texture"""
        self.textures[name] = texture

    def get_texture(self, name: str) -> Optional[moderngl.Texture]:
        """Get a texture by name"""
        return self.textures.get(name)

    def register_shader(self, name: str, shader: moderngl.Program):
        """Register a shader program"""
        self.shaders[name] = shader

    def get_shader(self, name: str) -> Optional[moderngl.Program]:
        """Get a shader program by name"""
        return self.shaders.get(name)

    def load_texture_from_file(self, name: str, filepath: str) -> moderngl.Texture:
        """Load a texture from file and register it"""
        # Implementation would use PIL or similar to load image
        # texture = self.ctx.texture(size, components, data)
        # self.textures[name] = texture
        # return texture
        pass

    def create_vao_from_mesh(self, name: str, vertices, indices, shader) -> moderngl.VertexArray:
        """Create a VAO from mesh data and register it"""
        vbo = self.ctx.buffer(vertices)
        ibo = self.ctx.buffer(indices) if indices is not None else None

        # This would need proper attribute setup based on shader
        vao = self.ctx.vertex_array(shader, [(vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_texcoord')], ibo)
        self.vaos[name] = vao
        return vao
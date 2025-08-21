
from typing import Dict, Optional, Any, List

from src4.components.component import Component


class Renderable(Component):
    """Complete rendering component for moderngl"""

    def __init__(self):
        # GPU resources (not serialized, rebuilt on load)
        self.vao = None  # moderngl.VertexArray
        self.shader_program = None  # moderngl.Program
        self.textures = {}  # Dict[str, moderngl.Texture] - e.g., {"diffuse": texture}

        # Serializable data
        self.mesh_name = ""  # Reference to mesh asset
        self.shader_name = "default"  # Reference to shader
        self.texture_names = {}  # Dict[str, str] - e.g., {"diffuse": "brick.png"}

        # Material properties
        self.material = {
            "albedo": [1.0, 1.0, 1.0],
            "metallic": 0.0,
            "roughness": 0.5,
            "emissive": [0.0, 0.0, 0.0],
            "alpha": 1.0
        }

        # Rendering settings
        self.visible = True  # Visibility is part of rendering
        self.cast_shadows = True
        self.receive_shadows = True
        self.render_order = 0  # For transparency sorting
        self.cull_face = True

        # Custom uniforms (for special effects, etc.)
        self.custom_uniforms = {}

    def set_uniform(self, name: str, value: Any):
        """Set a custom uniform value"""
        self.custom_uniforms[name] = value

    def apply_uniforms(self, world_matrix=None):
        """Apply all uniforms to the shader program"""
        if not self.shader_program:
            return

        # Set material uniforms
        if "material_albedo" in self.shader_program:
            self.shader_program["material_albedo"].value = self.material["albedo"]
        if "material_metallic" in self.shader_program:
            self.shader_program["material_metallic"].value = self.material["metallic"]
        if "material_roughness" in self.shader_program:
            self.shader_program["material_roughness"].value = self.material["roughness"]

        # Set world matrix if provided
        if world_matrix is not None and "model" in self.shader_program:
            import numpy as np
            # Convert to bytes for moderngl
            if hasattr(world_matrix, 'tobytes'):
                self.shader_program["model"].write(world_matrix.tobytes())
            else:
                self.shader_program["model"].write(np.array(world_matrix, dtype='f4').tobytes())

        # Bind textures
        for i, (slot, texture) in enumerate(self.textures.items()):
            if texture:
                texture.use(location=i)
                if f"texture_{slot}" in self.shader_program:
                    self.shader_program[f"texture_{slot}"].value = i

        # Apply custom uniforms
        for name, value in self.custom_uniforms.items():
            if name in self.shader_program:
                self.shader_program[name].value = value

    def render(self):
        """Execute the draw call"""
        if self.vao and self.shader_program:
            self.apply_uniforms()
            self.vao.render()

    def serialize(self) -> Dict[str, Any]:
        return {
            "mesh_name": self.mesh_name,
            "shader_name": self.shader_name,
            "texture_names": self.texture_names.copy(),
            "material": self.material.copy(),
            "visible": self.visible,
            "cast_shadows": self.cast_shadows,
            "receive_shadows": self.receive_shadows,
            "render_order": self.render_order,
            "cull_face": self.cull_face,
            "custom_uniforms": self.custom_uniforms.copy()
        }

    def deserialize(self, data: Dict[str, Any]):
        self.mesh_name = data.get("mesh_name", "")
        self.shader_name = data.get("shader_name", "default")
        self.texture_names = data.get("texture_names", {}).copy()
        self.material = data.get("material", self.material).copy()
        self.visible = data.get("visible", True)
        self.cast_shadows = data.get("cast_shadows", True)
        self.receive_shadows = data.get("receive_shadows", True)
        self.render_order = data.get("render_order", 0)
        self.cull_face = data.get("cull_face", True)
        self.custom_uniforms = data.get("custom_uniforms", {}).copy()

    def get_dirty_flags(self) -> List[str]:
        return ["render"]
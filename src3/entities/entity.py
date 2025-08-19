import moderngl
from typing import Optional
from glm import mat4

from src3.ubo_manager import UBOManager
from src3.shader_loader import ShaderLoader
from src3.components.mesh_component import MeshComponent
from src3.components.transform_component import TransformComponent
from src3.components.material_component import MaterialComponent
from src3.components.bezier_segment_component import BezierSegmentComponent
from src3.components.point_cloud_component import PointCloudComponent


class Entity:

    def __init__(self,
                 ctx: moderngl.Context,
                 shader_loader: ShaderLoader,
                 ubo_manager: UBOManager,
                 component_list: list,
                 label=None):

        self.ctx = ctx
        self.shader_loader = shader_loader
        self.ubo_manager = ubo_manager
        self.label = label if isinstance(label, str) else "entity"
        self.enabled = True

        # Components
        self.component_transform = None
        self.component_material = None
        self.component_mesh = None
        self.component_point_cloud = None
        self.component_bezier_segment = None

        self.scene_id: Optional[int] = None  # ID assigned by scene

        # Assign components
        for component in component_list:
            if isinstance(component, TransformComponent):
                self.component_transform = component
            elif isinstance(component, MaterialComponent):
                self.component_material = component
            elif isinstance(component, MeshComponent):
                self.component_mesh = component
            elif isinstance(component, PointCloudComponent):
                self.component_point_cloud = component
            elif isinstance(component, BezierSegmentComponent):
                self.component_bezier_segment = component

    def render(self, entity_id=None):
        pass

    def update(self, elapsed_time: float):
        pass

    def release(self):

        # Go over every component (that starts with "comp_") and release it if not None
        for attr_name in dir(self):
            if not attr_name.startswith("component_"):
                continue

            component = getattr(self, attr_name)
            if component is not None and hasattr(component, 'release'):
                component.release()

    def get_world_matrix(self) -> mat4:
        """Get world matrix (computed by scene hierarchy)"""
        if self.component_transform:
            return self.component_transform.world_matrix
        return mat4(1.0)

    def set_enabled(self, enabled: bool):
        """Enable/disable entity"""
        self.enabled = enabled

    def is_renderable(self) -> bool:
        """Check if entity should be rendered"""
        return bool(self.component_mesh or self.component_point_cloud)

import sys

import numpy as np
from core.window import Window
from core.shader_library import ShaderLibrary


class Renderer(object):

    def __init__(self, window: Window, shader_library: ShaderLibrary):

        self.window = window
        self.shader_library = shader_library

    def render(self, scene, flags, seg_node_map=None):

        # Update context with meshes and textures
        self._update_context(scene, flags)

        # Render necessary shadow maps
        if not bool(flags & RenderFlags.DEPTH_ONLY or flags & RenderFlags.SEG):
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

        # Make forward pass
        retval = self.render_pass_forward(scene, flags, seg_node_map=seg_node_map)

        # If necessary, make normals pass
        if flags & (RenderFlags.VERTEX_NORMALS | RenderFlags.FACE_NORMALS):
            self._normals_pass(scene, flags)

        # Update camera settings for retrieving depth buffers
        self._latest_znear = scene.main_camera_node.camera.znear
        self._latest_zfar = scene.main_camera_node.camera.zfar

        return retval

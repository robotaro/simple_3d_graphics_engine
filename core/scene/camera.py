from abc import ABC, abstractmethod


class CameraInterface(ABC):
    """
    An abstract class which describes the interface expected by the viewer for using this object as a camera
    """

    def __init__(self):
        self.projection_matrix = None
        self.view_matrix = None
        self.view_projection_matrix = None

    def get_projection_matrix(self):
        if self.projection_matrix is None:
            raise ValueError("update_matrices() must be called before to update the projection matrix")
        return self.projection_matrix

    def get_view_matrix(self):
        if self.view_matrix is None:
            raise ValueError("update_matrices() must be called before to update the view matrix")
        return self.view_matrix

    def get_view_projection_matrix(self):
        if self.view_projection_matrix is None:
            raise ValueError("update_matrices() must be called before to update the view-projection matrix")
        return self.view_projection_matrix

    @abstractmethod
    def update_matrices(self, width, height):
        pass

    @property
    @abstractmethod
    def position(self):
        pass

    @property
    @abstractmethod
    def forward(self):
        pass

    @property
    @abstractmethod
    def up(self):
        pass

    @property
    @abstractmethod
    def right(self):
        pass

    def gui(self, imgui):
        pass

class Camera:

    FOV = 50  # degrees
    NEAR = 0.1
    FAR = 100
    SPEED = 0.005
    SENSITIVITY = 0.04

    def __init__(self, app, position=(0, 0, 4), yaw=-90, pitch=0, ):
        self.app = app
        self.aspect_ratio = app.WIN_SIZE[0] / app.WIN_SIZE[1]
        self.position = glm.vec3(position)
        self.up = glm.vec3(0, 1, 0)
        self.right = glm.vec3(1, 0, 0)
        self.forward = glm.vec3(0, 0, -1)
        self.yaw = yaw
        self.pitch = pitch
        self.view_matrix = self.get_view_matrix()
        self.projection_matrix = self.get_projection_matrix()

    def rotate(self):
        delta_x, delta_y = pg.mouse.get_rel()
        self.yaw += delta_x * Camera.SENSITIVITY
        self.pitch -= delta_y * Camera.SENSITIVITY
        self.pitch = max(-89, min(89, self.pitch))

    def update_camera_vectors(self):
        yaw, pitch = glm.radians(self.yaw), glm.radians(self.pitch)

        self.forward.x = glm.cos(yaw) * glm.cos(pitch)
        self.forward.y = glm.sin(pitch)
        self.forward.z = glm.sin(yaw) * glm.cos(pitch)

        self.forward = glm.normalize(self.forward)
        self.right = glm.normalize(glm.cross(self.forward, glm.vec3(0, 1, 0)))  # default UP is (0, 1, 0)
        self.up = glm.normalize(glm.cross(self.right, self.forward))

    def update(self):
        self.move()
        self.rotate()
        self.update_camera_vectors()
        self.view_matrix = self.get_view_matrix()

    def move(self):
        velocity = Camera.SPEED * self.app.delta_time
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.position += self.forward * velocity
        if keys[pg.K_s]:
            self.position -= self.forward * velocity
        if keys[pg.K_a]:
            self.position -= self.right * velocity
        if keys[pg.K_d]:
            self.position += self.right * velocity
        if keys[pg.K_q]:
            self.position -= self.up * velocity
        if keys[pg.K_e]:
            self.position += self.up * velocity

    def get_view_matrix(self):
        return glm.lookAt(self.position, self.position + self.forward, self.up)

    def get_projection_matrix(self):
        return glm.perspective(glm.radians(Camera.FOV), self.aspect_ratio, Camera.NEAR, Camera.FAR)
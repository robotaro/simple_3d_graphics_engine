import numpy as np
from scipy.linalg import sqrtm
import time


class ShapeMatching:

    # All code was translated from :  /psystem.cpp

    def __init__(self):

        # Particles Positions
        self.particles_pos = np.ndarray((0, 3), dtype=np.float32)
        self.particles_pos_from_cm = np.ndarray((0, 3), dtype=np.float32)
        self.particles_initial_pos = np.ndarray((0, 3), dtype=np.float32)
        self.particles_initial_from_cm = np.ndarray((0, 3), dtype=np.float32)

        # My variables
        self.q_rel_pos_from_initial_cm = None
        self.p_rel_pos_from_cm = None

        #self.particles_pos_goal = np.ndarray((0, 3), dtype=np.float32)
        self.particles_past_pos = np.ndarray((0, 3), dtype=np.float32)

        # Particles Velocities
        self.particles_vel = np.ndarray((0, 3), dtype=np.float32)
        self.particles_past_vel = np.ndarray((0, 3), dtype=np.float32)

        # Center of mass
        self.center_of_mass = np.ndarray((0, 3), dtype=np.float32)  # Current center of Mass
        self.center_of_mass_initial = np.ndarray((0, 3), dtype=np.float32)  # Initial center Of Mass

        # Transformations
        self.mat_A = np.ndarray((3, 3), dtype=np.float32)
        self.mat_R = np.ndarray((3, 3), dtype=np.float32)
        self.mat_R_tilde = np.zeros((3, 9), dtype=np.float32)
        self.mat_A_pq = np.ndarray((3, 3), dtype=np.float32)
        self.mat_A_qq = np.ndarray((3, 3), dtype=np.float32)
        self.mat_A_tilde = np.zeros((3, 9), dtype=np.float32)
        self.mat_A_pq_tilde = np.zeros((3, 9), dtype=np.float32)
        self.mat_A_qq_tilde = np.ndarray((9, 9), dtype=np.float32)
        self.mat_q_tilde = np.ndarray((0, 9), dtype=np.float32)

        # Simulation variables
        self.alpha_stiffness = 0.2
        self.beta_bounciness = 0.5
        self.coeff_friction = 0.3

        # Enviroment variables
        self.gravity_vector = np.array([0, -9.81, 0], dtype=np.float32)
        self.floor_height = 0  # In the Y axis
        self.floor_normal = np.array([0, 1, 0], dtype=np.float32)

    def init(self, cube_rotation, cube_position, cube_scale=0.1, cube_size=5):

        if cube_size < 3:
            cube_size = 3

        self.particles_pos = self.build_cube(cube_rotation=cube_rotation,
                                             cube_position=cube_position,
                                             cube_scale=cube_scale,
                                             cube_size=cube_size)

        self.particles_pos = np.matmul(cube_rotation, self.particles_pos.T).T
        self.particles_pos += cube_position

        # Centre of mass of initial position
        self.center_of_mass = np.mean(self.particles_pos, axis=0)
        self.center_of_mass_initial = self.center_of_mass.copy()

        self.particles_initial_from_cm = self.particles_pos - self.center_of_mass

        q_x = self.particles_initial_from_cm[:, 0]
        q_y = self.particles_initial_from_cm[:, 1]
        q_z = self.particles_initial_from_cm[:, 2]

        self.mat_q_tilde[:, 0] = q_x
        self.mat_q_tilde[:, 1] = q_y
        self.mat_q_tilde[:, 2] = q_z
        self.mat_q_tilde[:, 3] = q_x * q_x
        self.mat_q_tilde[:, 4] = q_y * q_y
        self.mat_q_tilde[:, 5] = q_z * q_z
        self.mat_q_tilde[:, 6] = q_x * q_y
        self.mat_q_tilde[:, 7] = q_y * q_z
        self.mat_q_tilde[:, 8] = q_z * q_x

        # Calculate A_QQ
        #self.mat_A_qq = np.matmul(self.particles_initial_pos_rel.T, self.particles_initial_pos_rel)
        #self.mat_A_qq = np.linalg.inv(self.mat_A_qq)

        # Calculate A_QQ method v
        sum = np.zeros((3, 3), dtype=np.float32)
        for pos in self.particles_initial_from_cm:
            sum += np.outer(pos, pos)
        self.mat_A_qq = np.linalg.inv(sum)

        # Calculate A_QQ_tilde
        #self.mat_A_qq_tilde = np.matmul(self.mat_q_tilde.T, self.mat_q_tilde) # I may have to transpose this!
        #self.mat_A_qq_tilde = np.linalg.inv(self.mat_A_qq_tilde)

        sum = np.zeros((9, 9), dtype=np.float32)
        for pos in self.mat_q_tilde:
            sum += np.outer(pos, pos)
        self.mat_A_qq_tilde = np.linalg.inv(sum)

        # Finialize value initialization
        self.particles_pos_from_cm[:] = self.particles_initial_from_cm

    def update(self, delta_t, use_verlet=False):

        # Update positions and velocities using Verlet integration
        self.particles_past_pos[:] = self.particles_pos
        self.particles_past_vel[:] = self.particles_vel
        if use_verlet:
            self.particles_vel += self.gravity_vector * delta_t
            self.particles_pos += (self.particles_past_vel + self.particles_vel) * 0.5 * delta_t
        else:
            pass

        # Update center of mass and particles relative positions to it
        self.center_of_mass = np.mean(self.particles_pos, axis=0)
        self.particles_initial_from_cm = self.particles_pos - self.center_of_mass

        # Calculate A_pq matrix
        #self.mat_A_pq = np.matmul(self.particles_pos_rel.T, self.particles_initial_pos_rel)
        #self.mat_A = np.matmul(self.mat_A_pq, self.mat_A_qq)
        sum = np.zeros((3, 3), dtype=np.float32)
        for pos in self.particles_pos_from_cm:
            sum += np.outer(pos, pos)
        self.mat_A_pq = sum
        self.mat_A = np.matmul(sum, self.mat_A_qq)
        self.mat_A /= np.cbrt(np.linalg.det(self.mat_A))

        # Calculate S and R matrices
        mat_S = sqrtm(np.matmul(self.mat_A_pq.T, self.mat_A_pq))
        self.mat_R = np.linalg.inv(mat_S)

        # Calculate R_tilde
        self.mat_R_tilde[:, 0:3] = self.mat_R

        # Calculate A_pq_tilde
        self.mat_A_pq_tilde = np.matmul(self.particles_pos_from_cm.T, self.mat_q_tilde)

        # Calculate A_tilde
        self.mat_A_tilde = np.matmul(self.mat_A_pq_tilde, self.mat_A_qq_tilde)

        # Fix A with volume preservation (again ?)
        mat_goal = self.beta_bounciness * self.mat_A_tilde + (1 - self.beta_bounciness) * self.mat_R_tilde
        inv_dt = 1.0 / delta_t

        goal = np.matmul(mat_goal, self.mat_q_tilde.T).T + self.center_of_mass
        alpha_change = self.alpha_stiffness * (goal - self.particles_pos) * inv_dt

        self.particles_vel += alpha_change
        self.particles_pos = self.particles_past_pos + self.particles_vel * delta_t

        # ============ COLISION DETECTION =================
        # Idea from: https://github.com/mshooter/smd/blob/master/deformationLib/src/Particle.cpp
        colision_mask = self.particles_pos[:, 1] <= self.floor_height
        self.particles_pos[colision_mask, 1] = 0
        self.particles_vel[colision_mask, 1] = 0

    def build_cube(self, cube_rotation, cube_position, cube_scale=0.1, cube_size=5):

        # Demo parameters
        cube_dim = np.array([cube_size, cube_size, cube_size], dtype=np.int32)
        cube_dim_internal = cube_dim - 2

        cube = np.ones((cube_dim[0], cube_dim[1], cube_dim[2]))
        offset = cube_dim_internal + 1
        cube[1:offset[0], 1:offset[1], 1:offset[2]] = 0
        num_particles = np.sum(cube == 1)

        particles = np.ndarray((num_particles, 3), dtype=np.float32)
        index = 0
        for i in range(cube_dim[0]):
            for j in range(cube_dim[1]):
                for k in range(cube_dim[2]):
                    if cube[i, j, k] == 1:
                        particles[index, :] = [i, j, k]
                        index += 1

        particles *= cube_scale

        return particles



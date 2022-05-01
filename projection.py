import math
from OpenGL import GLUT
import numpy as np


class Projection:
    def __init__(self):
        self.fov_rad: float = np.deg2rad(90)

    def set_projection(self, fov_deg: float):
        self.fov_rad = np.deg2rad(fov_deg)

    def get_projection_matrix(self, width=None, height=None):
        if not width:
            width = GLUT.glutGet(GLUT.GLUT_WINDOW_WIDTH)
        if not height:
            height = GLUT.glutGet(GLUT.GLUT_WINDOW_HEIGHT)
        ar = width / height

        near_z = 1
        far_z = 10
        z_range = near_z - far_z
        A = (-far_z - near_z) / z_range
        B = (2 * near_z * far_z) / z_range

        tan_half_fov = math.tan(self.fov_rad / 2)
        f = 1 / tan_half_fov

        return np.matrix([
            [f / ar, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, A, B],
            [0, 0, 1, 0]
        ], dtype=np.float32)

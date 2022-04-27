import math
import numpy as np
from OpenGL import GLUT


class Pipeline:
    def __init__(self):
        self.scaling = np.identity(4)
        self.translation = np.identity(4)
        self.rotation = np.identity(4)
        self.projection = np.identity(4)
        return

    def rotate_xz(self, deg: int):
        self.rotation = np.matrix([
            [math.cos(deg), 0, -1 * math.sin(deg), 0],
            [0, 1, 0, 0],
            [math.sin(deg), 0, math.cos(deg), 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

    def scale(self, scale: float):
        self.scaling = np.matrix([
            [math.sin(scale), 0, 0, 0],
            [0, math.sin(scale), 0, 0],
            [0, 0, math.sin(scale), 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

    def move(self, x, y, z):
        self.translation = np.matrix([
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1]
        ], dtype=np.float32)

    def project_xy(self, fov_deg: float):
        ar = GLUT.glutGet(GLUT.GLUT_WINDOW_WIDTH) / \
            GLUT.glutGet(GLUT.GLUT_WINDOW_HEIGHT)

        near_z = 1
        far_z = 10
        z_range = near_z - far_z
        A = (-far_z - near_z) / z_range
        B = (2 * near_z * far_z) / z_range

        fov_rad = np.deg2rad(fov_deg)
        tan_half_fov = math.tan(fov_rad / 2)
        f = 1 / tan_half_fov

        self.projection = np.matrix([
            [f / ar, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, A, B],
            [0, 0, 1, 0]
        ], dtype=np.float32)

    def getTranslationMatrix(self):
        trans = np.identity(4, dtype=np.float32)
        trans = trans * self.projection
        trans = trans * self.translation
        trans = trans * self.rotation
        trans = trans * self.scaling

        return trans

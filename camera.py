import numpy as np
import math
from OpenGL import GLUT


class Camera:
    def __init__(self, pos=None, target=None, up=None):
        self.speed = 0.2
        self.pos = np.array([0, 0, 0], dtype=np.float32)
        self.target = target if target is not None else np.array(
            [0, 0, 1], dtype=np.float32)
        self.target = self.target / np.linalg.norm(self.target, ord=1)
        self.up = up if up is not None else np.array(
            [0, 1, 0], dtype=np.float32)
        self.angle_h = 0
        self.angle_v = 0
        self.mouse_x = 0
        self.mouse_y = 0

        self.init_camera()

        # GLUT.glutWarpPointer(self.mouse_x, self.mouse_y)

    def init_camera(self):
        h_target = np.array(
            [self.target[0], 0, self.target[2]], dtype=np.float32)
        angle = np.rad2deg(math.asin(abs(h_target[2])))
        if (h_target[2] >= 0):
            if (h_target[0] >= 0):
                self.angle_h = 360 - angle
            else:
                self.angle_h = 180 + angle
        else:
            if (h_target < 0):
                self.angle_h = angle
            else:
                self.angle_h = 180 - angle

        self.angle_v = np.rad2deg(math.asin(self.target[1]))

        # self.mouse_x = int(GLUT.glutGet(GLUT.GLUT_WINDOW_WIDTH) / 2)
        # self.mouse_y = int(GLUT.glutGet(GLUT.GLUT_WINDOW_HEIGHT) / 2)

        return

    def set_pos(self, x, y, z):
        self.pos = np.array([x, y, z], dtype=np.float32)

    def set_up(self, x, y, z):
        self.up = np.array([x, y, z], dtype=np.float32)

    def handle_keyboard(self, key, x, y):
        if key == GLUT.GLUT_KEY_UP:
            self.pos += self.target * self.speed
        elif key == GLUT.GLUT_KEY_DOWN:
            self.pos -= self.target * self.speed
        elif key == GLUT.GLUT_KEY_LEFT:
            left = np.cross(self.target, self.up)
            left = left / np.linalg.norm(left, ord=1)
            left *= self.speed
            self.pos += left
        elif key == GLUT.GLUT_KEY_RIGHT:
            right = np.cross(self.up, self.target)
            right = right / np.linalg.norm(right, ord=1)
            right = right * self.speed
            self.pos += right
        elif key == GLUT.GLUT_KEY_PAGE_UP:
            self.pos += np.array(0, self.speed, 0)
        elif key == GLUT.GLUT_KEY_PAGE_DOWN:
            self.pos -= np.array(0, self.speed, 0)
        elif chr(key) == '+':
            self.speed += 0.1
        elif chr(key) == '-':
            self.speed -= 0.1
            if self.speed < 0.1:
                self.speed = 0.1

    def handle_mouse(self, x, y):
        # mouse_delta_x = x - self.mouse_x
        # mouse_delta_y = y - self.mouse_y
        # self.mouse_x, self.mouse_y = x, y

        # self.angle_h += mouse_delta_x / 20
        # self.angle_v += mouse_delta_y / 50
        pass
    
    def update(self):
        pass

    def get_matrix(self):
        N = self.target / np.linalg.norm(self.target, ord=1)
        U = np.cross(self.up, self.target)
        U = U / np.linalg.norm(U, ord=1)
        V = np.cross(N, U)

        return np.matrix(
            [[*U, self.pos[0]],
             [*V, self.pos[1]],
             [*N, self.pos[2]],
             [0, 0, 0, 1]], dtype=np.float32
        )

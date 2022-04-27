import math
import numpy as np


class World:
    ROTATE_XY = 0
    ROTATE_XZ = 1
    ROTATE_YZ = 2

    def __init__(self):
        self._scale = np.identity(4)
        self._position = np.identity(4)
        self._rotation = np.identity(4)

    def set_scale(self, scale: float):
        self._scale = np.matrix([
            [math.sin(scale), 0, 0, 0],
            [0, math.sin(scale), 0, 0],
            [0, 0, math.sin(scale), 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

    def set_position(self, x: float, y: float, z: float):
        self._position = np.matrix([
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1]
        ], dtype=np.float32)

    def set_rotation(self, rad: float, axis: int):
        if (axis > self.ROTATE_YZ):
            raise ValueError("Invalid rotation value")

        if axis == self.ROTATE_XY:
            self._rotation = np.matrix(
                [[math.cos(rad), -1 * math.sin(rad), 0, 0],
                 [math.sin(rad), math.cos(rad), 0, 0],
                 [0, 0, 1, 0],
                 [0, 0, 0, 1]], dtype=np.float32
            )
        elif axis == self.ROTATE_YZ:
            self._rotation = np.matrix([
                [math.cos(rad), 0, -1 * math.sin(rad), 0],
                [0, 1, 0, 0],
                [math.sin(rad), 0, math.cos(rad), 0],
                [0, 0, 0, 1]
            ], dtype=np.float32)
        elif axis == self.ROTATE_XZ:
            self._rotation = np.matrix([
                [1, 0, 0, 0],
                [0, math.cos(rad), -1 * math.sin(rad), 0],
                [0, math.sin(rad), math.cos(rad), 0],
                [0, 0, 0, 1]
            ], dtype=np.float32)

    def get_world_translation(self):
        return self._position * self._rotation * self._scale

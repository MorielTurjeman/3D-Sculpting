import ctypes
from distutils.ccompiler import new_compiler
from itertools import cycle
import numpy as np
from random import seed, random
from OpenGL import GL

seed()


class Vertex:
    STRIDE = ctypes.sizeof(ctypes.c_float) * 5
    POS_OFFSET = ctypes.c_void_p(0)
    TEXTURE_OFFSET = ctypes.c_void_p(3 * ctypes.sizeof(ctypes.c_float))

    last_id = 0

    def __init__(self, x, y, z, texture_vec, buf=None):
        self.val = np.empty(6, dtype=np.float32) if buf is None else buf
        self.pos = self.val[:3] = np.array([x, y, z], dtype=np.float32)
        self.val[3:5] = texture_vec

    def set_coords(self, x, y, z):
        self.val[:3] = np.array([x, y, z], dtype=np.float32)

    def move(self, x, y, z):
        translation = np.matrix(
            [
                [1, 0, 0, x],
                [0, 1, 0, y],
                [0, 0, 1, z],
                [0, 0, 0, 1]
            ]
        )

        pos = np.array([*self.val[:3], 1], dtype=np.float32)

        new_coords = np.dot(translation, pos)
        new_coords = [new_coords[0, 0], new_coords[0, 1], new_coords[0, 2]]
        self.val[:3] = new_coords[:3]

    def __sizeof__(self) -> int:
        return ctypes.sizeof(ctypes.c_float) * (2 + 3)

    @classmethod
    def set_attrib_array(cls):
        # position
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(
            0, 3, GL.GL_FLOAT, GL.GL_FALSE, Vertex.STRIDE, Vertex.POS_OFFSET)

        # color
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(
            1, 2, GL.GL_FLOAT, GL.GL_FALSE, Vertex.STRIDE,
            Vertex.TEXTURE_OFFSET)

    @classmethod
    def next_class_id(cls):
        id, cls.last_id = cls.last_id, cls.last_id + 1
        return id

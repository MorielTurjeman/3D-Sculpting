from abc import ABC, abstractmethod
import numpy as np
from vertex import Vertex


class Model(ABC):
    @abstractmethod
    def get_vertex_array(self):
        pass

    @abstractmethod
    def get_index_array(self):
        pass

    @abstractmethod
    def set_vertex(self, vertex_id, x, y, z):
        pass

    @abstractmethod
    def move_vertex_in_vector(self, vertex_id, x, y, z):
        pass


class Cube(Model):
    def __init__(self):
        super().__init__()

        self.data = np.empty(8 * 5, dtype=np.float32)

        t00 = np.array([0, 0], dtype=np.float32)
        t01 = np.array([0, 1], dtype=np.float32)
        t10 = np.array([1, 0], dtype=np.float32)
        t11 = np.array([1, 1], dtype=np.float32)

        self.vertices = [
            Vertex(0.5, 0.5, 0.5, t00, self.data[0*5:1*5]),
            Vertex(-0.5, 0.5, -0.5, t01, self.data[1*5:2*5]),
            Vertex(-0.5, 0.5, 0.5, t10, self.data[2*5:3*5]),
            Vertex(0.5, -0.5, -0.5, t11, self.data[3*5:4*5]),
            Vertex(-0.5, -0.5, -0.5, t00, self.data[4*5:5*5]),
            Vertex(0.5, 0.5, -0.5, t01, self.data[5*5:6*5]),
            Vertex(0.5, -0.5, 0.5, t10, self.data[6*5:7*5]),
            Vertex(-0.5, -0.5, 0.5, t11, self.data[7*5:])
        ]

        self.indices = np.array(
            [0, 1, 2,
             1, 3, 4,
             5, 6, 3,
             7, 3, 6,
             2, 4, 7,
             0, 7, 6,
             0, 5, 1,
             1, 5, 3,
             5, 0, 6,
             7, 4, 3,
             2, 1, 4,
             0, 2, 7
             ], dtype=np.uint32
        )

    def get_index_array(self):
        return self.indices

    def get_vertex_array(self):
        return self.data

    def set_vertex(self, vertex_id, x, y, z):
        for v in self.vertices:
            if v.id == vertex_id:
                self.vertices[vertex_id].set_coords(x, y, z)

    def move_vertex_in_vector(self, vertex_id, x, y, z):
        self.vertices[vertex_id].move(x, y, z)

from typing import List
from camera import Camera
from cube import Model
from mouse_picker import PickingTexture
from texture import Texture
from glsl_program import ShaderCodlet
from OpenGL import GL
from projection import Projection
from vertex import Vertex
from world import World

import numpy as np


class Framebuffer(ShaderCodlet):

    def __init__(self, world: World, projection: Projection,
                 camera: Camera, texture: Texture):

        super().__init__()

        self.translationMatLocation = None
        self.world = world
        self.projection = projection
        self.camera = camera
        self.texture = texture
        self.rotation_scale = 0

        self.fbo = GL.glGenFramebuffers(1)
        self.vbo = GL.glGenBuffers(1)
        self.iao = GL.glGenBuffers(1)
        self.vao = GL.glGenVertexArrays(1)

        self.program.add_shader_from_file("shader.vs", GL.GL_VERTEX_SHADER)
        self.program.add_shader_from_file("shader.fs", GL.GL_FRAGMENT_SHADER)

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.iao)

        self.models: List[Model] = []

    def write_buffers(self):
        for model in self.models:
            GL.glBufferData(
                GL.GL_ARRAY_BUFFER,
                np.array(model.get_vertex_array(), dtype=np.float32),
                GL.GL_DYNAMIC_DRAW
            )
            GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER,
                            model.get_index_array(),
                            GL.GL_STATIC_DRAW)

    def add_model(self, model: Model):
        self.models.append(model)

    def compile_shaders(self):
        if len(self.models) == 0:
            return

        self.program.compile_and_use_program()

        self.translationMatLocation = \
            self.program.get_uniform_location('translationMat')

        # self.sampler_location = self.program.get_uniform_location('sampler2')

    def set_projection_matrix(self, translation_matrix):
        GL.glUniformMatrix4fv(self.translationMatLocation, 1,
                              GL.GL_TRUE, translation_matrix)

    def render(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        translationMatrix = self.projection.get_projection_matrix() * \
            self.camera.get_matrix() * \
            self.world.get_world_translation()

        GL.glUniformMatrix4fv(self.translationMatLocation, 1,
                              GL.GL_TRUE, translationMatrix)

        # GL.glUniform1i(self.sampler_location, 0)
        # self.rotation_scale += 0.02
        # self.world.set_rotation(self.rotation_scale, axis=World.ROTATE_YZ)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.iao)
        self.texture.bind(GL.GL_TEXTURE0)

        Vertex.set_attrib_array()

        GL.glDrawElements(GL.GL_TRIANGLES, 36, GL.GL_UNSIGNED_INT, None)
        GL.glDisableVertexAttribArray(0)
        GL.glDisableVertexAttribArray(1)

    def picking_render(self, texture: PickingTexture):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        translationMatrix = self.projection.get_projection_matrix() * \
            self.camera.get_matrix() * \
            self.world.get_world_translation()

        GL.glUniformMatrix4fv(self.translationMatLocation, 1,
                              GL.GL_TRUE, translationMatrix)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.iao)

        Vertex.set_attrib_array()

        GL.glDrawElements(GL.GL_POINTS, 36, GL.GL_UNSIGNED_INT, None)
        GL.glDisableVertexAttribArray(0)
        GL.glDisableVertexAttribArray(1)

    def get_world_coord(self, window_coord):
        window_coord = [
            (window_coord[0] - 400) / 400,
            (window_coord[1] - 400) / 400, 0, 1
            ]
        projection_view_matrix = np.linalg.inv(
            np.dot(self.projection.get_projection_matrix(), self.camera.get_matrix()))

        world_coord = np.dot(projection_view_matrix, window_coord)
        world_coord = np.array([
            world_coord[0, 0],
            world_coord[0, 1],
            world_coord[0, 2],
            world_coord[0, 3]
        ], dtype=np.float32)

        world_coord = world_coord / world_coord[3]

        return world_coord

    def get_model_coord(self, window_coord):
        world_coord = self.get_world_coord(window_coord)
        inv_world_trans = np.linalg.inv(self.world.get_world_translation())
        model_coord = np.dot(inv_world_trans, world_coord)
        model_coord = np.array([
            model_coord[0, 0],
            model_coord[0, 1],
            model_coord[0, 2],
            model_coord[0, 3]
        ])

        model_coord = model_coord / model_coord[3]
        

        return model_coord




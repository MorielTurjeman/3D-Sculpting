from OpenGL import GL, GLUT
from camera import Camera

from glsl_program import ShaderCodlet
from projection import Projection
from texture import Texture
from vertex import Vertex
from world import World


class PickingTechnique(ShaderCodlet):
    VS = '''
            #version 330

            layout (location = 0) in vec3 Position;

            uniform mat4 gWVP;

            void main()
            {
                gl_Position = gWVP * vec4(Position, 1.0);
            }
         '''

    FS = '''
            #version 330

            uniform uint gDrawIndex;
            uniform uint gObjectIndex;

            out vec3 FragColor;

            void main()
            {
                FragColor = vec3(float(gObjectIndex), float(gDrawIndex),float(gl_PrimitiveID + 1));
            }
         '''

    def __init__(self, world: World, projection: Projection,
                 camera: Camera):

        super().__init__()

        self.translationMatLocation = None
        self.world = world
        self.projection = projection
        self.camera = camera
        self.rotation_scale = 0

        self.program.add_shader(self.VS, shader_type=GL.GL_VERTEX_SHADER)
        self.program.add_shader(self.FS, shader_type=GL.GL_FRAGMENT_SHADER)

        self.program.compile_and_use_program()

        self.wvp_matrix_loction = GL.glGetUniformLocation("gWVP")
        self.object_index_location = GL.glGetUniformLocation("gObjectIndex")
        self.draw_index_location = GL.glGetUniformLocation('gDrawIndex')

    def render(self, width, height):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        translationMatrix = \
            self.projection.get_projection_matrix(width, height) * \
            self.camera.get_matrix() * \
            self.world.get_world_translation()

        GL.glUniformMatrix4fv(self.translationMatLocation, 1,
                              GL.GL_TRUE, translationMatrix)

        # GL.glUniform1i(self.gSamplerLocation, 0)
        # self.rotation_scale += 0.02
        # self.world.set_rotation(self.rotation_scale, axis=World.ROTATE_YZ)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.iao)
        self.texture.bind(GL.GL_TEXTURE0)

        Vertex.set_attrib_array()

        GL.glDrawElements(GL.GL_TRIANGLES, 36, GL.GL_UNSIGNED_INT, None)
        GL.glDisableVertexAttribArray(0)
        GL.glDisableVertexAttribArray(1)


class PickingTexture:
    def __init__(self):
        screen_width = GLUT.glutGet(GLUT.GLUT_WINDOW_WIDTH)
        screen_height = GLUT.glutGet(GLUT.GLUT_WINDOW_HEIGHT)

        self.fbo = GL.glGenFramebuffers(1)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.fbo)
        # create primitive texture object
        self.picking_texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.picking_texture)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGB32F, screen_width,
                        screen_height, 0, GL.GL_RGB, GL.GL_FLOAT, None)

        # create depth buffer texture object
        self.depth_texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.depth_texture)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_DEPTH_COMPONENT,
                        screen_width, screen_height,
                        0, GL.GL_DEPTH_COMPONENT, GL.GL_FLOAT, None)
        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_DEPTH_ATTACHMENT,
                                  GL.GL_TEXTURE_2D, self.depth_texture, 0)

        GL.glReadBuffer(GL.GL_NONE)
        GL.glDrawBuffer(GL.GL_COLOR_ATTACHMENT0)

        status = GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER)

        if status != GL.GL_FRAMEBUFFER_COMPLETE:
            print(f"FB error, status: {status:x}\n")
            return False

        # Restore the default framebuffer
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

        return GL.GLCheckError()

    def enable_writing(self):
        GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, self.fbo)

    def disable_writing(self):
        GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, None)

    def read_pixel(self, x, y):
        GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, self.fbo)
        GL.glReadBuffer(GL.GL_COLOR_ATTACHMENT0)

        pixel_info = GL.glReadPixels(x, y, 1, 1, GL.GL_RGB, GL.GL_FLOAT)
        print(pixel_info)

        GL.glReadBuffer(GL.GL_NONE)
        GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, None)

        return pixel_info

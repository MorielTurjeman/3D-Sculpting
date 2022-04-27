from cgitb import text
from OpenGL import GL, GLUT


class PickingTexture:
    def __init__(self, height: int, width: int):
        self.fbo = GL.glGenFramebuffers(1)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.fbo)

        self.target = GL.GL_TEXTURE_2D
        self.texture = GL.glGenTextures(1)
        GL.glBindTexture(self.target, self.texture)
        GL.glTexImage2D(self.target, 0, GL.GL_R32I, height, width,
                        0, GL.GL_RED_INTEGER, GL.GL_UNSIGNED_BYTE, None)
        GL.glTexParameteri(self.target, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(self.target, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(self.target, GL.GL_TEXTURE_WRAP_R,
                           GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(self.target, GL.GL_TEXTURE_WRAP_S,
                           GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(self.target, GL.GL_TEXTURE_WRAP_T,
                           GL.GL_CLAMP_TO_EDGE)

        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT1,
                                  GL.GL_TEXTURE_2D, self.texture, 0)
        GL.glReadBuffer(GL.GL_NONE)

        GL.glDrawBuffers(2, [GL.GL_COLOR_ATTACHMENT0, GL.GL_COLOR_ATTACHMENT1])

        status = GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER)
        if (status != GL.GL_FRAMEBUFFER_COMPLETE):
            print(f"FB error, status {status}")
            raise RuntimeError(status)

        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

    def get_target(self):
        return self.target

    def read_texture(self, x, y):
        GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, self.fbo)
        GL.glReadBuffer(GL.GL_COLOR_ATTACHMENT1)
        pixelData = GL.glReadPixels(x, y, 1, 1, GL.GL_RED_INTEGER, GL.GL_INT)
        GL.glReadBuffer(GL.GL_NONE)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
        print(pixelData)
        [pixel_id] = pixelData[0]
        if pixel_id == 0:
            return -1
        else:
            return pixel_id - 1

    def bind(self, texture_unit):
        GL.glActiveTexture(texture_unit)
        GL.glBindTexture(self.target, self.texture)


class MouseHandler:
    def __init__(self):
        self.texture = PickingTexture(800, 800)
        self.selected_window_coord = None

    def handle_mouse(self, x, y):
        return self.texture.read_texture(x, y)
   
    def enable_writing(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, self.texture.fbo)

    def disable_writing(self):
        GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, 0)

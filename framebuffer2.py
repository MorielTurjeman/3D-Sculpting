from typing import Text
from OpenGL import GL
from texture import Texture

class FrameBuffer2:
    def __init__(self):
        self.fbo = GL.glGenFramebuffers(1)
        self.textures = []
        
    def bind(self):
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.fbo)
    
    def unbind(self):
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

    def read_pixel(self, id, x, y):
        GL.glReadBuffer(id)
        pixel_data = GL.glReadPixels(x, y, 1, 1, GL.GL_RED_INTEGER, GL.GL_INT)
        return pixel_data

    def attach_texture(self, texture: Texture):
        GL.glBindTexture(texture.target, texture.id)
        if (texture.img_data):
            GL.glTexImage2D(texture.target, 0, GL.GL_RGB, texture.width, texture.height,
                            0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, texture.img_data)
        else:
            GL.glTexImage2D(texture.target, 0, GL.GL_R32I, texture.width, texture.height,
                            0, GL.GL_RED_INTEGER, GL.GL_UNSIGNED_BYTE, texture.img_data)
        GL.glTexParameterf(texture.target, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameterf(texture.target, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameterf(texture.target, GL.GL_TEXTURE_WRAP_S,
                           GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameterf(texture.target, GL.GL_TEXTURE_WRAP_T,
                           GL.GL_CLAMP_TO_EDGE)
        GL.glBindTexture(texture.target, 0)

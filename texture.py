from OpenGL import GL
from PIL import Image
import numpy as np


class Texture:
    def __init__(self, path: str, target: int):
        self.path = path
        self.target = target
        self.texture = None
        pass

    def load(self):
        img = Image.open(self.path)
        img = img.convert('RGB')
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = np.array(list(img.getdata()), np.uint8)
        height, width = img.size
        print(height, width)
        self.texture = GL.glGenTextures(1)

        GL.glBindTexture(self.target, self.texture)
        # GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)

        # GL.glTexImage2D(self.target, 0, GL.GL_RGBA, width, height,
        #                 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, img_data)

        GL.glTexParameterf(self.target, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameterf(self.target, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameterf(self.target, GL.GL_TEXTURE_WRAP_S,
                           GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameterf(self.target, GL.GL_TEXTURE_WRAP_T,
                           GL.GL_CLAMP_TO_EDGE)

        GL.glBindTexture(self.target, 0)
        return True

    def bind(self, texture_unit):
        GL.glActiveTexture(texture_unit)
        GL.glBindTexture(self.target, self.texture)

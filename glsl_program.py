from typing import List
from OpenGL import GL


class ShaderCodlet():

    def __init__(self):
        self.program = GLSLProgram()

    def render(self):
        return None


class GLSLProgram:

    def __init__(self):
        self.program = GL.glCreateProgram()
        self.compiled = False
        self.codelets: List[ShaderCodlet] = []

    def add_shader(self, shader_text: str,
                   shader_type):
        shader_obj = GL.glCreateShader(shader_type)
        if (shader_type is None):
            raise ValueError("Could not create shader")

        GL.glShaderSource(shader_obj, [shader_text])
        GL.glCompileShader(shader_obj)
        status = GL.glGetShaderiv(shader_obj, GL.GL_COMPILE_STATUS)
        if not status:
            log = GL.glGetShaderInfoLog(shader_obj)
            print(log)
            raise RuntimeError("Could not compile shader")

        GL.glAttachShader(self.program, shader_obj)

    def add_shader_from_file(self, shader_path: str, shader_type):
        with open(shader_path, "r") as shader:
            vs = shader.read()
            self.add_shader(vs, shader_type)
            return

    def get_uniform_location(self, uniform_name: str):
        if not self.compiled:
            raise RuntimeError("GLSL program not compiled yet")
        location = GL.glGetUniformLocation(
            self.program, uniform_name)

        if location < 0:
            raise ValueError(f"Could not location {uniform_name} in program")

        return location

    def add_shader_codlet(self, codelet):
        self.codelets.append(codelet)

    def compile_and_use_program(self):
        for codelet in self.codelets:
            codelet.add_codlet_shaders(glsl_program=self)

        GL.glLinkProgram(self.program)
        status = GL.glGetProgramiv(self.program, GL.GL_LINK_STATUS)
        if not status:
            log = GL.glGetProgramInfoLog(self.program)
            print(log)
            raise RuntimeError("Could not compile shader program")
        GL.glValidateProgram(self.program)
        status = GL.glGetProgramiv(self.program, GL.GL_VALIDATE_STATUS)
        if not status:
            log = GL.glGetProgramInfoLog(self.program)
            print(log)
            raise RuntimeError("Could not validate shader program")
        GL.glUseProgram(self.program)
        self.compiled = True

        for codelet in self.codelets:
            codelet.read_variables_location(glsl_program=self)

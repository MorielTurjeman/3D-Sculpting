import trimesh
from trimesh.visual import to_rgba
from trimesh import rendering
from OpenGL import GL as gl
from OpenGL import GLU as glu
import numpy as np

class GlManager:
    def __init__(self, scene: trimesh.Scene, line_setting):
        self.background = None
        self.scene = scene
        self.line_settings = line_setting
        return

    def reset_gl(self):
        # if user passed a background color use it
        if self.background is None:
            # default background color is white
            background = np.ones(4)
        else:
            # convert to (4,) uint8 RGBA
            background = to_rgba(self.background)
            # convert to 0.0-1.0 float
            background = background.astype(np.float64) / 255.0

        self.set_background(background)
        # use camera setting for depth
        self.enable_depth(self.scene.camera)
        self.enable_color_material()
        self.enable_blending()
        self.enable_smooth_lines(**self.line_settings)
        self.enable_lighting(self.scene)


    @staticmethod
    def set_background(background):
        gl.glClearColor(*background)

    @staticmethod
    def _gl_unset_background():
        gl.glClearColor(*[0, 0, 0, 0])

    @staticmethod
    def enable_depth(camera):
        # set the culling depth from our camera object
        gl.glDepthRange(camera.z_near, camera.z_far)

        gl.glClearDepth(1.0)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LEQUAL)

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)

    @staticmethod
    def enable_color_material():
        # do some openGL things
        gl.glColorMaterial(gl.GL_FRONT_AND_BACK,
                           gl.GL_AMBIENT_AND_DIFFUSE)
        gl.glEnable(gl.GL_COLOR_MATERIAL)
        gl.glShadeModel(gl.GL_SMOOTH)

        gl.glMaterialfv(gl.GL_FRONT,
                        gl.GL_AMBIENT,
                        rendering.vector_to_gl(
                            0.192250, 0.192250, 0.192250))
        gl.glMaterialfv(gl.GL_FRONT,
                        gl.GL_DIFFUSE,
                        rendering.vector_to_gl(
                            0.507540, 0.507540, 0.507540))
        gl.glMaterialfv(gl.GL_FRONT,
                        gl.GL_SPECULAR,
                        rendering.vector_to_gl(
                            .5082730, .5082730, .5082730))

        gl.glMaterialf(gl.GL_FRONT,
                       gl.GL_SHININESS,
                       .4 * 128.0)

    @staticmethod
    def enable_blending():
        # enable blending for transparency
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA,
                       gl.GL_ONE_MINUS_SRC_ALPHA)

    @staticmethod
    def enable_smooth_lines(line_width=4, point_size=4):
        # make the lines from Path3D objects less ugly
        gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST)
        # set the width of lines to 4 pixels
        gl.glLineWidth(line_width)
        # set PointCloud markers to 4 pixels in size
        gl.glPointSize(point_size)

    @staticmethod
    def enable_lighting(scene):
        """
        Take the lights defined in scene.lights and
        apply them as openGL lights.
        """
        gl.glEnable(gl.GL_LIGHTING)
        # opengl only supports 7 lights?
        for i, light in enumerate(scene.lights[:7]):
            # the index of which light we have
            lightN = eval('gl.GL_LIGHT{}'.format(i))

            # get the transform for the light by name
            matrix = scene.graph.get(light.name)[0]

            # convert light object to glLightfv calls
            multiargs = rendering.light_to_gl(
                light=light,
                transform=matrix,
                lightN=lightN)

            # enable the light in question
            gl.glEnable(lightN)
            # run the glLightfv calls
            for args in multiargs:
                gl.glLightfv(*args)


    def set_modelview_matrix(self, width, height):
        # set the new viewport size
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()

        # get field of view and Z range from camera
        camera = self.scene.camera

        # set perspective from camera data
        glu.gluPerspective(camera.fov[1],
                          width / float(height),
                          camera.z_near,
                          camera.z_far)
        gl.glMatrixMode(gl.GL_MODELVIEW)

        return width, height

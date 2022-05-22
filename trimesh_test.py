"""
windowed.py
---------------

Provides a pyglet- based windowed viewer to preview
Trimesh, Scene, PointCloud, and Path objects.

Works on all major platforms: Windows, Linux, and OSX.
"""
import sys
import threading
import multiprocessing
import collections
from graphviz import view
from matplotlib.pyplot import sca
# from graphviz import view
import numpy as np
from app import init_camera_window, main

import pyglet
from pyglet.window import Window
from imgui.integrations.pyglet import PygletRenderer


import imgui
from trimesh.viewer.trackball import Trackball
from OpenGL.GL import *
from OpenGL.GLU import *

import trimesh
import trimesh.collision
import trimesh.ray
import trimesh.creation
import trimesh.remesh
from trimesh import Trimesh, util
from trimesh import rendering, Scene
from trimesh.scene import Camera

from trimesh.visual import to_rgba
from trimesh.transformations import translation_matrix
#from hand_gesture_recognition.hand_functions import *

pyglet.options['shadow_window'] = True

import pyglet.gl as gl  # NOQA


# smooth only when fewer faces than this
_SMOOTH_MAX_FACES = 100000


class UI:
    def __init__(self, window):
        imgui.create_context()
        self.renderer = PygletRenderer(window)
        self.impl = PygletRenderer(window)
        imgui.new_frame()
        imgui.end_frame()

        # Window variables

        self.window: SceneViewer = window
        self.test_input = 0

    def render(self):
        imgui.render()
        io = imgui.get_io()
        self.impl.render(imgui.get_draw_data())

        checkbox_smoothing = True
        

        imgui.new_frame()
        scene: Scene = self.window.scene
        imgui.begin("Design Window", flags=imgui.WINDOW_MENU_BAR)
        imgui.text("Brushes!!!")
        imgui.button("Brush 1")
        imgui.button("Brush 2")
        imgui.button("Brush 3")

        checkbox_smoothing = imgui.checkbox("Smoothing", checkbox_smoothing) # create smoothign checkbox
        
        imgui.button("Zoom in")
        imgui.button("Zoom out")
        imgui.button("Strech in")
        imgui.button("Strech out")

        x_rotation_value = 88
        y_rotation_value = 88
        z_rotation_value = 88

        changed, values = imgui.slider_float(
        "X rotation", x_rotation_value,
        min_value=0.0, max_value=100.0,
        format="%.0f",
        power=0.5
        )
    
        # imgui.text("Changed: %s, Values: %s" % (changed, value))

        changed, values = imgui.slider_float(
        "Y rotation", y_rotation_value,
        min_value=0.0, max_value=100.0,
        format="%.0f",
        power=0.5
        )
        if changed:
            y_rotation_value = values

        changed, values = imgui.slider_float(
        "Z rotation", z_rotation_value,
        min_value=0.0, max_value=100.0,
        format="%.0f",
        power=0.5
        )
        
        
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("Primitives", True):
                clicked, selected = imgui.menu_item(
                    'Capsule', None, False, True)
                if clicked:
                    scene.geometry.popitem()
                    capsule = trimesh.primitives.Capsule()
                    scene.add_geometry(capsule)
                    self.window.reset_view()
                clicked, selected = imgui.menu_item("Cube")
                if clicked:
                    scene.geometry.popitem()
                    box = trimesh.primitives.Box()
                    scene.add_geometry(box)
                    self.window.reset_view()
                clicked, selected = imgui.menu_item("Sphere")
                if clicked:
                    scene.geometry.popitem()
                    sphere = trimesh.primitives.Sphere()
                    scene.add_geometry(sphere)
                    self.window.reset_view()
                imgui.end_menu()

            if imgui.begin_menu("Actions", True):
                clicked, selected = imgui.menu_item("Strech in")
                if clicked:
                    # //call strech in function
                    pass
                clicked, selected = imgui.menu_item("Strech out")
                if clicked:
                    # //call strech out function
                    pass
                imgui.end_menu()

            if imgui.begin_menu("Mode", True):
                clicked, selected = imgui.menu_item("Hands")
                if clicked:
                    #
                    pass
                clicked, selected = imgui.menu_item("Mouse")
                if clicked:
                    #
                    pass
                imgui.end_menu()

            if imgui.begin_menu("Project", True):
                clicked, selected = imgui.menu_item("Start over")
                if clicked:
                    self.window.reset_view()
                clicked, selected = imgui.menu_item("Quit")
                if clicked:
                    sys.exit(0)
                imgui.end_menu()

            imgui.end_main_menu_bar()

        imgui.end()

        scale_x_val = 0.0
        scale_y_val = 0.0
        scale_z_val = 0.0
        imgui.begin("Scale")
        # changed, values = imgui.input_float4('Type here:', *values)
        # imgui.text("Changed: %s, Values: %s" % (changed, values))
        changed, float_val = imgui.input_float('X', scale_x_val)
        changed, float_val = imgui.input_float('Y', scale_y_val)
        changed, float_val = imgui.input_float('Z', scale_z_val)
        imgui.end()

        imgui.end_frame()


class SceneViewer(pyglet.window.Window):

    def __init__(self,
                 scene,
                 smooth=True,
                 flags=None,
                 visible=True,
                 resolution=None,
                 start_loop=True,
                 callback=None,
                 callback_period=None,
                 caption=None,
                 fixed=None,
                 offset_lines=True,
                 line_settings=None,
                 background=None,
                 window_conf=None,
                 profile=False,
                 record=False,
                 **kwargs):
        """
        Create a window that will display a trimesh.Scene object
        in an OpenGL context via pyglet.

        Parameters
        ---------------
        scene : trimesh.scene.Scene
          Scene with geometry and transforms
        smooth : bool
          If True try to smooth shade things
        flags : dict
          If passed apply keys to self.view:
          ['cull', 'wireframe', etc]
        visible : bool
          Display window or not
        resolution : (2,) int
          Initial resolution of window
        start_loop : bool
          Call pyglet.app.run() at the end of init
        callback : function
          A function which can be called periodically to
          update things in the scene
        callback_period : float
          How often to call the callback, in seconds
        fixed : None or iterable
          List of keys in scene.geometry to skip view
          transform on to keep fixed relative to camera
        offset_lines : bool
          If True, will offset lines slightly so if drawn
          coplanar with mesh geometry they will be visible
        background : None or (4,) uint8
          Color for background
        window_conf : None, or gl.Config
          Passed to window init
        profile : bool
          If set will run a `pyinstrument` profile for
          every call to `on_draw` and print the output.
        record : bool
          If True, will save a list of `png` bytes to
          a list located in `scene.metadata['recording']`
        kwargs : dict
          Additional arguments to pass, including
          'background' for to set background color
        """
        self.scene = self._scene = scene

        self.callback = callback
        self.callback_period = callback_period
        self.scene._redraw = self._redraw
        self.offset_lines = bool(offset_lines)
        self.background = background
        # save initial camera transform
        self._initial_camera_transform = scene.camera_transform.copy()
        self.selected_vertex = None
        self.selected_vertex_world = None
        self.selected_vertex_z = None

        # a transform to offset lines slightly to avoid Z-fighting
        self._line_offset = translation_matrix(
            [0, 0, scene.scale / 1000 if self.offset_lines else 0])

        self.reset_view()
        self.batch = pyglet.graphics.Batch()
        self._smooth = smooth

        self._profile = bool(profile)

        self._record = bool(record)
        if self._record:
            # will save bytes here
            self.scene.metadata['recording'] = []

        # store kwargs
        self.kwargs = kwargs

        # store a vertexlist for an axis marker
        self._axis = None
        # store a vertexlist for a grid display
        self._grid = None
        # store scene geometry as vertex lists
        self.vertex_list = {}
        # store geometry hashes
        self.vertex_list_hash = {}
        # store geometry rendering mode
        self.vertex_list_mode = {}
        # store meshes that don't rotate relative to viewer
        self.fixed = fixed
        # store a hidden (don't not display) node.
        self._nodes_hidden = set()
        # name : texture
        self.textures = {}

        # if resolution isn't defined set a default value
        if resolution is None:
            resolution = scene.camera.resolution
        else:
            scene.camera.resolution = resolution

        # set the default line settings to a fraction
        # of our resolution so the points aren't tiny
        scale = max(resolution)
        self.line_settings = {'point_size': scale / 200,
                              'line_width': scale / 400}
        # if we've been passed line settings override the default
        if line_settings is not None:
            self.line_settings.update(line_settings)

        # no window conf was passed so try to get the best looking one
        if window_conf is None:
            try:
                # try enabling antialiasing
                # if you have a graphics card this will probably work
                conf = gl.Config(sample_buffers=1,
                                 samples=4,
                                 depth_size=24,
                                 double_buffer=True)
                super(SceneViewer, self).__init__(config=conf,
                                                  visible=visible,
                                                  resizable=True,
                                                  width=resolution[0],
                                                  height=resolution[1],
                                                  caption=caption)
            except pyglet.window.NoSuchConfigException:
                conf = gl.Config(double_buffer=True)
                super(SceneViewer, self).__init__(config=conf,
                                                  resizable=True,
                                                  visible=visible,
                                                  width=resolution[0],
                                                  height=resolution[1],
                                                  caption=caption)
        else:
            # window config was manually passed
            super(SceneViewer, self).__init__(config=window_conf,
                                              resizable=True,
                                              visible=visible,
                                              width=resolution[0],
                                              height=resolution[1],
                                              caption=caption)

        # add scene geometry to viewer geometry
        self._update_vertex_list()

        # call after geometry is added
        self.init_gl()
        self.set_size(*resolution)
        if flags is not None:
            self.reset_view(flags=flags)
        self.update_flags()

        # someone has passed a callback to be called periodically
        if self.callback is not None:
            # if no callback period is specified set it to default
            if callback_period is None:
                # 30 times per second
                callback_period = 1.0 / 30.0
            # set up a do-nothing periodic task which will
            # trigger `self.on_draw` every `callback_period`
            # seconds if someone has passed a callback
            pyglet.clock.schedule_interval(lambda x: x,
                                           callback_period)

        self.ui = UI(self)

    def _redraw(self):
        self.on_draw()

    def _update_vertex_list(self):
        # update vertex_list if needed
        for name, geom in self.scene.geometry.items():
            if geom.is_empty:
                continue
            if geometry_hash(geom) == self.vertex_list_hash.get(name):
                continue
            self.add_geometry(name=name,
                              geometry=geom,
                              smooth=bool(self._smooth))

    def _update_meshes(self):
        # call the callback if specified
        if self.callback is not None:
            self.callback(self.scene)
        self._update_vertex_list()
        self._update_perspective(self.width, self.height)

    def add_geometry(self, name, geometry, **kwargs):
        """
        Add a geometry to the viewer.

        Parameters
        --------------
        name : hashable
          Name that references geometry
        geometry : Trimesh, Path2D, Path3D, PointCloud
          Geometry to display in the viewer window
        kwargs **
          Passed to rendering.convert_to_vertexlist
        """
        try:
            # convert geometry to constructor args
            args = rendering.convert_to_vertexlist(geometry, **kwargs)
        except BaseException:
            util.log.warning('failed to add geometry `{}`'.format(name),
                             exc_info=True)
            return

        # create the indexed vertex list
        self.vertex_list[name] = self.batch.add_indexed(*args)
        # save the hash of the geometry
        self.vertex_list_hash[name] = geometry_hash(geometry)
        # save the rendering mode from the constructor args
        self.vertex_list_mode[name] = args[1]

        try:
            # if a geometry has UV coordinates that match vertices
            assert len(geometry.visual.uv) == len(geometry.vertices)
            has_tex = True
        except BaseException:
            has_tex = False

        if has_tex:
            tex = rendering.material_to_texture(
                geometry.visual.material)
            if tex is not None:
                self.textures[name] = tex

    def cleanup_geometries(self):
        """
        Remove any stored vertex lists that no longer
        exist in the scene.
        """
        # shorthand to scene graph
        graph = self.scene.graph
        # which parts of the graph still have geometry
        geom_keep = set([graph[node][1] for
                         node in graph.nodes_geometry])
        # which geometries no longer need to be kept
        geom_delete = [geom for geom in self.vertex_list
                       if geom not in geom_keep]
        for geom in geom_delete:
            # remove stored vertex references
            self.vertex_list.pop(geom, None)
            self.vertex_list_hash.pop(geom, None)
            self.vertex_list_mode.pop(geom, None)
            self.textures.pop(geom, None)

    def unhide_geometry(self, node):
        """
        If a node is hidden remove the flag and show the
        geometry on the next draw.

        Parameters
        -------------
        node : str
          Node to display
        """
        self._nodes_hidden.discard(node)

    def hide_geometry(self, node):
        """
        Don't display the geometry contained at a node on
        the next draw.

        Parameters
        -------------
        node : str
          Node to not display
        """
        self._nodes_hidden.add(node)

    def reset_view(self, flags=None):
        """
        Set view to the default view.

        Parameters
        --------------
        flags : None or dict
          If any view key passed override the default
          e.g. {'cull': False}
        """
        self.view = {
            'cull': True,
            'axis': False,
            'grid': False,
            'fullscreen': False,
            'wireframe': False,
            'ball': Trackball(
                pose=self._initial_camera_transform,
                size=self.scene.camera.resolution,
                scale=self.scene.scale,
                target=self.scene.centroid)}
        try:
            # if any flags are passed override defaults
            if isinstance(flags, dict):
                for k, v in flags.items():
                    if k in self.view:
                        self.view[k] = v
                self.update_flags()
        except BaseException:
            pass

    def init_gl(self):
        """
        Perform the magic incantations to create an
        OpenGL scene using pyglet.
        """

        # if user passed a background color use it
        if self.background is None:
            # default background color is white
            background = np.ones(4)
        else:
            # convert to (4,) uint8 RGBA
            background = to_rgba(self.background)
            # convert to 0.0-1.0 float
            background = background.astype(np.float64) / 255.0

        self._gl_set_background(background)
        # use camera setting for depth
        self._gl_enable_depth(self.scene.camera)
        self._gl_enable_color_material()
        self._gl_enable_blending()
        self._gl_enable_smooth_lines(**self.line_settings)
        self._gl_enable_lighting(self.scene)

    @staticmethod
    def _gl_set_background(background):
        gl.glClearColor(*background)

    @staticmethod
    def _gl_unset_background():
        gl.glClearColor(*[0, 0, 0, 0])

    @staticmethod
    def _gl_enable_depth(camera):
        """
        Enable depth test in OpenGL using distances
        from `scene.camera`.
        """
        # set the culling depth from our camera object
        gl.glDepthRange(camera.z_near, camera.z_far)

        gl.glClearDepth(1.0)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LEQUAL)

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)

    @staticmethod
    def _gl_enable_color_material():
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
    def _gl_enable_blending():
        # enable blending for transparency
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA,
                       gl.GL_ONE_MINUS_SRC_ALPHA)

    @staticmethod
    def _gl_enable_smooth_lines(line_width=4, point_size=4):
        # make the lines from Path3D objects less ugly
        gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST)
        # set the width of lines to 4 pixels
        gl.glLineWidth(line_width)
        # set PointCloud markers to 4 pixels in size
        gl.glPointSize(point_size)

    @staticmethod
    def _gl_enable_lighting(scene):
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

    def toggle_culling(self):
        """
        Toggle back face culling.

        It is on by default but if you are dealing with
        non- watertight meshes you probably want to be able
        to see the back sides.
        """
        self.view['cull'] = not self.view['cull']
        self.update_flags()

    def toggle_wireframe(self):
        """
        Toggle wireframe mode

        Good for  looking inside meshes, off by default.
        """
        self.view['wireframe'] = not self.view['wireframe']
        self.update_flags()

    def toggle_fullscreen(self):
        """
        Toggle between fullscreen and windowed mode.
        """
        self.view['fullscreen'] = not self.view['fullscreen']
        self.update_flags()

    def toggle_axis(self):
        """
        Toggle a rendered XYZ/RGB axis marker:
        off, world frame, every frame
        """
        # cycle through three axis states
        states = [False, 'world', 'all', 'without_world']
        # the state after toggling
        index = (states.index(self.view['axis']) + 1) % len(states)
        # update state to next index
        self.view['axis'] = states[index]
        # perform gl actions
        self.update_flags()

    def toggle_grid(self):
        """
        Toggle a rendered grid.
        """
        # update state to next index
        self.view['grid'] = not self.view['grid']
        # perform gl actions
        self.update_flags()

    def update_flags(self):
        """
        Check the view flags, and call required GL functions.
        """
        # view mode, filled vs wirefrom
        if self.view['wireframe']:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        else:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

        # set fullscreen or windowed
        self.set_fullscreen(fullscreen=self.view['fullscreen'])

        # backface culling on or off
        if self.view['cull']:
            gl.glEnable(gl.GL_CULL_FACE)
        else:
            gl.glDisable(gl.GL_CULL_FACE)

        # case where we WANT an axis and NO vertexlist
        # is stored internally
        if self.view['axis'] and self._axis is None:
            from trimesh import creation
            # create an axis marker sized relative to the scene
            axis = creation.axis(origin_size=self.scene.scale / 100)
            # create ordered args for a vertex list
            args = rendering.mesh_to_vertexlist(axis)
            # store the axis as a reference
            self._axis = self.batch.add_indexed(*args)
        # case where we DON'T want an axis but a vertexlist
        # IS stored internally
        elif not self.view['axis'] and self._axis is not None:
            # remove the axis from the rendering batch
            self._axis.delete()
            # set the reference to None
            self._axis = None

        if self.view['grid'] and self._grid is None:
            try:
                # create a grid marker
                from trimesh.path.creation import grid
                bounds = self.scene.bounds
                center = bounds.mean(axis=0)
                # set the grid to the lowest Z position
                # also offset by the scale to avoid interference
                center[2] = bounds[0][2] - (bounds[:, 2].ptp() / 100)
                # choose the side length by maximum XY length
                side = bounds.ptp(axis=0)[:2].max()
                # create an axis marker sized relative to the scene
                grid_mesh = grid(
                    side=side,
                    count=4,
                    transform=translation_matrix(center))
                # convert the path to vertexlist args
                args = rendering.convert_to_vertexlist(grid_mesh)
                # create ordered args for a vertex list
                self._grid = self.batch.add_indexed(*args)
            except BaseException:
                util.log.warning(
                    'failed to create grid!', exc_info=True)
        elif not self.view['grid'] and self._grid is not None:
            self._grid.delete()
            self._grid = None

    def _update_perspective(self, width, height):
        try:
            # for high DPI screens viewport size
            # will be different then the passed size
            width, height = self.get_viewport_size()
        except BaseException:
            # older versions of pyglet may not have this
            pass

        # set the new viewport size
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()

        # get field of view and Z range from camera
        camera = self.scene.camera

        # set perspective from camera data
        gl.gluPerspective(camera.fov[1],
                          width / float(height),
                          camera.z_near,
                          camera.z_far)
        gl.glMatrixMode(gl.GL_MODELVIEW)

        return width, height

    def on_resize(self, width, height):
        """
        Handle resized windows.
        """
        width, height = self._update_perspective(width, height)
        self.scene.camera.resolution = (width, height)
        self.view['ball'].resize(self.scene.camera.resolution)
        self.scene.camera_transform[...] = self.view['ball'].pose

    def on_mouse_press(self, x, y, buttons, modifiers):
        """
        Set the start point of the drag.
        """
        self.view['ball'].set_state(Trackball.STATE_ROTATE)
        if (buttons == pyglet.window.mouse.LEFT):
            ctrl = (modifiers & pyglet.window.key.MOD_CTRL)
            shift = (modifiers & pyglet.window.key.MOD_SHIFT)
            alt= (modifiers & pyglet.window.key.MOD_ALT)
            if alt:
                self.select_vertex()
            elif (ctrl and shift):
                self.view['ball'].set_state(Trackball.STATE_ZOOM)
            elif shift:
                self.view['ball'].set_state(Trackball.STATE_ROLL)
            elif ctrl:
                self.view['ball'].set_state(Trackball.STATE_PAN)
        elif (buttons == pyglet.window.mouse.MIDDLE):
            self.view['ball'].set_state(Trackball.STATE_PAN)
        elif (buttons == pyglet.window.mouse.RIGHT):
            self.view['ball'].set_state(Trackball.STATE_ZOOM)

        self.view['ball'].down(np.array([x, y]))
        self.scene.camera_transform[...] = self.view['ball'].pose

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """
        Pan or rotate the view.
        """
        if self.selected_vertex:
            self.drag_vertex()
        else:
            self.view['ball'].drag(np.array([x, y]))
            self.scene.camera_transform[...] = self.view['ball'].pose

    def on_mouse_scroll(self, x, y, dx, dy):
        """
        Zoom the view.
        """
        self.view['ball'].scroll(dy)
        self.scene.camera_transform[...] = self.view['ball'].pose
        print(dy)
    
    def on_mouse_release(self, x, y, button, modifiers):
        self.selected_vertex= None

    def on_key_press(self, symbol, modifiers):
        """
        Call appropriate functions given key presses.
        """
        magnitude = 10
        if symbol == pyglet.window.key.W:
            self.toggle_wireframe()
        elif symbol == pyglet.window.key.Z:
            self.reset_view()
        elif symbol == pyglet.window.key.C:
            self.toggle_culling()
        elif symbol == pyglet.window.key.A:
            self.toggle_axis()
        elif symbol == pyglet.window.key.G:
            self.toggle_grid()
        elif symbol == pyglet.window.key.Q:
            self.on_close()
        elif symbol == pyglet.window.key.M:
            self.maximize()
        elif symbol == pyglet.window.key.F:
            self.toggle_fullscreen()
        elif symbol == pyglet.window.key.S:
            self.select_vertex()
        elif symbol == pyglet.window.key.L:
            self.drag_vertex()
        elif symbol == pyglet.window.key.P:
            self.collide_with_sphere()
        elif symbol== pyglet.window.key.I:
            self.scale()

        if symbol in [
                pyglet.window.key.LEFT,
                pyglet.window.key.RIGHT,
                pyglet.window.key.DOWN,
                pyglet.window.key.UP]:
            self.view['ball'].down([0, 0])
            if symbol == pyglet.window.key.LEFT:
                self.view['ball'].drag([-magnitude, 0])
            elif symbol == pyglet.window.key.RIGHT:
                self.view['ball'].drag([magnitude, 0])
            elif symbol == pyglet.window.key.DOWN:
                self.view['ball'].drag([0, -magnitude])
            elif symbol == pyglet.window.key.UP:
                self.view['ball'].drag([0, magnitude])
            self.scene.camera_transform[...] = self.view['ball'].pose

    # def scale(self):
    #     scene: Scene = self.scene
    #     geom: Trimesh = scene.geometry.get('geometry_0')
    #     geom.apply_scale([ 0.2, 0.3, 0])



    def collision(self):
        x = int(self._mouse_x)
        y = int(self._mouse_y)
        z0 = (GLfloat * 1)()
        # read the pixels to identify depth of drawn pixel
        glReadPixels(x, y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT, z0)
        px = (GLdouble)()
        py = (GLdouble)()
        pz = (GLdouble)()
        # convert pixel to world coordinates, if data is not empty, you will see 'normal' values (small sizes)
        coord = gluUnProject(x, y, z0[0])

        scene: Scene = self.scene
        geom: Trimesh = scene.geometry.get('geometry_0')
        selected = None

        # find the closes vertex to the pixel
        for i, v in enumerate(geom.vertices):
            dist = float(np.linalg.norm(v - coord))
            print(dist, v)
            if dist < 0.1:
                print(f"here {i}")
                selected = i

        # print vertex
        if selected is not None:
            print(f"selected vertex: {geom.vertices[selected]}")

    def on_draw(self):
        """
        Run the actual draw calls.
        """

        if self._profile:
            profiler = self.Profiler()
            profiler.start()

        self._update_meshes()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()

        # pull the new camera transform from the scene
        transform_camera = np.linalg.inv(self.scene.camera_transform)

        # apply the camera transform to the matrix stack
        gl.glMultMatrixf(rendering.matrix_to_gl(transform_camera))

        # we want to render fully opaque objects first,
        # followed by objects which have transparency
        node_names = collections.deque(self.scene.graph.nodes_geometry)
        # how many nodes did we start with
        count_original = len(node_names)
        count = -1

        # if we are rendering an axis marker at the world
        if self._axis and not self.view['axis'] == 'without_world':
            # we stored it as a vertex list
            self._axis.draw(mode=gl.GL_TRIANGLES)
        if self._grid:
            self._grid.draw(mode=gl.GL_LINES)

        # save a reference outside of the loop
        geometry = self.scene.geometry
        graph = self.scene.graph

        while len(node_names) > 0:
            count += 1
            current_node = node_names.popleft()

            if current_node in self._nodes_hidden:
                continue

            # get the transform from world to geometry and mesh name
            transform, geometry_name = graph.get(current_node)

            # if no geometry at this frame continue without rendering
            if geometry_name is None or geometry_name not in self.vertex_list_mode:
                continue

            # if a geometry is marked as fixed apply the inverse view transform
            if self.fixed is not None and geometry_name in self.fixed:
                # remove altered camera transform from fixed geometry
                transform_fix = np.linalg.inv(
                    np.dot(self._initial_camera_transform, transform_camera))
                # apply the transform so the fixed geometry doesn't move
                transform = np.dot(transform, transform_fix)

            # get a reference to the mesh so we can check transparency
            mesh = geometry.get(geometry_name)
            if mesh is None or mesh.is_empty:
                continue

            # get the GL mode of the current geometry
            mode = self.vertex_list_mode[geometry_name]

            # if you draw a coplanar line with a triangle it will z-fight
            # the best way to do this is probably a shader but this works fine
            if mode == gl.GL_LINES:
                # apply the offset in camera space
                transform = util.multi_dot([
                    transform,
                    np.linalg.inv(transform_camera),
                    self._line_offset,
                    transform_camera])

            # add a new matrix to the model stack
            gl.glPushMatrix()
            # transform by the nodes transform
            gl.glMultMatrixf(rendering.matrix_to_gl(transform))

            # draw an axis marker for each mesh frame
            if self.view['axis'] == 'all':
                self._axis.draw(mode=gl.GL_TRIANGLES)
            elif self.view['axis'] == 'without_world':
                if not util.allclose(transform, np.eye(4), atol=1e-5):
                    self._axis.draw(mode=gl.GL_TRIANGLES)

            # transparent things must be drawn last
            if (hasattr(mesh, 'visual') and
                hasattr(mesh.visual, 'transparency')
                    and mesh.visual.transparency):
                # put the current item onto the back of the queue
                if count < count_original:
                    # add the node to be drawn last
                    node_names.append(current_node)
                    # pop the matrix stack for now
                    gl.glPopMatrix()
                    # come back to this mesh later
                    continue

            # if we have texture enable the target texture
            texture = None
            if geometry_name in self.textures:
                texture = self.textures[geometry_name]
                gl.glEnable(texture.target)
                gl.glBindTexture(texture.target, texture.id)

            # draw the mesh with its transform applied
            self.vertex_list[geometry_name].draw(mode=mode)
            # pop the matrix stack as we drew what we needed to draw
            gl.glPopMatrix()

            # disable texture after using
            if texture is not None:
                gl.glDisable(texture.target)

        if self._profile:
            profiler.stop()
            print(profiler.output_text(unicode=True, color=True))

        self.ui.render()

    def flip(self):
        super(SceneViewer, self).flip()
        if self._record:
            # will save a PNG-encoded bytes
            img = self.save_image(util.BytesIO())
            # seek start of file-like object
            img.seek(0)
            # save the bytes from the file object
            self.scene.metadata['recording'].append(img.read())

    def save_image(self, file_obj):
        """
        Save the current color buffer to a file object
        in PNG format.

        Parameters
        -------------
        file_obj: file name, or file- like object
        """
        manager = pyglet.image.get_buffer_manager()
        colorbuffer = manager.get_color_buffer()
        # if passed a string save by name
        if hasattr(file_obj, 'write'):
            colorbuffer.save(file=file_obj)
        else:
            colorbuffer.save(filename=file_obj)
        return file_obj

    def get_mouse_coords(self):
        deviceWidth, _ = self.get_framebuffer_size()
        widthRatio = deviceWidth / self.width
        x = int(self._mouse_x * widthRatio)
        y = int(self._mouse_y * widthRatio)

        return x, y

    def get_z_for_coord(self, x, y):
        # read the pixels to identify depth of drawn pixel, if no pixel is found we will get a very 'distant' z

        z0 = (GLfloat * 1)()
        glReadPixels(x, y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT, z0)

        return z0[0]

    def select_vertex(self):
        x, y = self.get_mouse_coords()
        z = self.get_z_for_coord(x, y)

        # convert pixel to world coordinates, if data is not empty, you will see 'normal' values (small sizes)
        coord = gluUnProject(x, y, z)

        scene: Scene = self.scene
        geom: Trimesh = scene.geometry.get('geometry_0')
        for i, v in enumerate(geom.vertices):
            dist = float(np.linalg.norm(v - coord))
            if dist < 0.1:
                self.selected_vertex = i
                self.selected_vertex_world = coord
                self.selected_vertex_z = z

        print(
            f"Selecting vertex: {self.selected_vertex}, coords: {self.selected_vertex_world}")

    def drag_vertex(self):
        if self.selected_vertex is None:
            print("no selected vertex")
            return
        scene: Scene = self.scene
        geom: Trimesh = scene.geometry.get('geometry_0')
        x, y = self.get_mouse_coords()
        # z = self.get_z_for_coord(x, y)
        coords = gluUnProject(x, y, self.selected_vertex_z)
        geom.vertices[self.selected_vertex] = coords

        trimesh.smoothing.filter_taubin(geom)

    def collide_with_sphere(self):
        x, y = self.get_mouse_coords()
        z = self.get_z_for_coord(x, y)
        cx, cy, cz = gluUnProject(x, y, z)
        sphere = trimesh.primitives.Sphere(center=[cx, cy, cz], radius=0.1)
        scene: Scene = self.scene
        geom: Trimesh = scene.geometry['geometry_0']
        mask = sphere.contains(geom.vertices)
        for i, m in enumerate(mask):
            if m:
                v = geom.vertices[i]
                d = v - sphere.center_mass
                geom.vertices[i] += d

        trimesh.smoothing.filter_taubin(geom)


def geometry_hash(geometry):
    """
    Get a hash for a geometry object

    Parameters
    ------------
    geometry : object

    Returns
    ------------
    hash : str
    """
    if hasattr(geometry, 'crc'):
        # for most of our trimesh objects
        h = str(geometry.crc())
    elif hasattr(geometry, 'md5'):
        h = geometry.md5()
    elif hasattr(geometry, 'tostring'):
        # for unwrap ndarray objects
        h = str(hash(geometry.tostring()))

    if hasattr(geometry, 'visual'):
        # if visual properties are defined
        h += str(geometry.visual.crc())
    elif hasattr(geometry, 'visual_crc'):
        # paths do not use the visual attribute
        h += str(geometry.colors_crc())

    return h


def render_scene(scene,
                 resolution=None,
                 visible=True,
                 **kwargs):
    """
    Render a preview of a scene to a PNG. Note that
    whether this works or not highly variable based on
    platform and graphics driver.

    Parameters
    ------------
    scene : trimesh.Scene
      Geometry to be rendered
    resolution : (2,) int or None
      Resolution in pixels or set from scene.camera
    visible : bool
      Show a window during rendering. Note that MANY
      platforms refuse to render with hidden windows
      and will likely return a blank image; this is a
      platform issue and cannot be fixed in Python.
    kwargs : **
      Passed to SceneViewer

    Returns
    ---------
    render : bytes
      Image in PNG format
    """
    window = SceneViewer(
        scene, start_loop=False, visible=visible,
        resolution=resolution, **kwargs)

    from trimesh.util import BytesIO

    # need to run loop twice to
    # ay anything
    for save in [False, False, True]:
        pyglet.clock.tick()
        window.switch_to()
        window.dispatch_events()
        window.dispatch_event('on_draw')
        window.flip()
        if save:
            # save the color buffer data to memory
            file_obj = BytesIO()
            window.save_image(file_obj)
            file_obj.seek(0)
            render = file_obj.read()
    window.close()

    return render


def init_3d():
    box = trimesh.creation.box()
    box.vertices, box.faces = trimesh.remesh.subdivide_to_size(
        box.vertices, box.faces, 0.1)
    scene = Scene(box)
    viewer = SceneViewer(scene)
    init_camera_window(viewer.on_mouse_press,
                       viewer.on_mouse_drag, viewer.on_mouse_scroll)
    # handgest=Hand_handler(viewer)
    pyglet.app.run()  # blocking!!!!!!!!!


if __name__ == '__main__':
    init_3d()
    pyglet.app.run()
    p1 = multiprocessing.Process(target=main, args=(state,))

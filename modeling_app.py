"""
windowed.py
---------------

Provides a pyglet- based windowed viewer to preview
Trimesh, Scene, PointCloud, and Path objects.

Works on all major platforms: Windows, Linux, and OSX.
"""
from copy import deepcopy
from curses import window
from sre_constants import CHCODES
import sys
import threading
import multiprocessing
import collections
from cv2 import gemm
# from graphviz import view
import numpy as np
import scipy
import scipy.spatial
from app import init_camera_window

import pyglet
import pyglet.window.mouse
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

from state_manager import StateManager

from gl_manager import GlManager
#from hand_gesture_recognition.hand_functions import *

pyglet.options['shadow_window'] = True
pyglet.options['debug_gl'] = False
pyglet.options['xsync'] = False

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
        self.checkbox_smoothing = False
        self.x_rotation_value = 0
        self.y_rotation_value = 0
        self.z_rotation_value = 0
        self.scale_x_val = 1.0
        self.scale_y_val = 1.0
        self.scale_z_val = 1.0
        self.ignore_clicks = False

    def render(self):
        self.ignore_clicks = False
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
        imgui.render()
        io = imgui.get_io()
        self.impl.render(imgui.get_draw_data())
        imgui.new_frame()
        #set size for all the widget sliders
        # imgui.begin_child("region", 200, -50, border=False)


        scene: Scene = self.window.scene
        geometry: Trimesh = scene.geometry.get('geometry_0')
        trans = np.identity((4), dtype=np.float64)
    

        imgui.begin("Design Window", flags=imgui.WINDOW_MENU_BAR)


       
        imgui.text("Brushes!!!")
        if (imgui.button("Brush 1")):
            self.window.set_mouse_brush_sphere(1)
        if imgui.button("Brush 2"):
            self.window.set_mouse_brush_sphere(3)
        if imgui.button("Brush 3"):
            self.window.set_mouse_brush_sphere(5)

        # if checkbox_smoothing:
        _, self.checkbox_smoothing = imgui.checkbox(
            "Smoothing", self.checkbox_smoothing)  # create smoothign

        imgui.button("Zoom in")
        imgui.button("Zoom out")
        imgui.button("Strech in")
        imgui.button("Strech out")
        #set size for all the widget sliders
        # imgui.begin_child("region", 200, -50, border=False)
        _, self.scale_x_val = imgui.input_float('X scale', self.scale_x_val, format="%.2f")
        _, self.scale_y_val = imgui.input_float('Y scale', self.scale_y_val, format="%.2f")
        _, self.scale_z_val = imgui.input_float('Z scale', self.scale_z_val, format="%.2f")
        self.window.scale(self.scale_x_val, self.scale_y_val, self.scale_z_val)

       
        changed, x_rotation_value = imgui.slider_float(
        "X rotation", self.x_rotation_value,
        min_value=-180, max_value=180.0,
        format="%.0f",
        power=0.5
        )
        self.ignore_clicks = self.ignore_clicks or imgui.is_item_active()
        r = np.deg2rad(x_rotation_value - self.x_rotation_value)
        self.x_rotation_value = x_rotation_value
        # print(r)
        if changed:
            trans = np.dot(trans, np.array(
                [
                    [np.cos(r), 0, -1 * np.sin(r), 0 ],
                    [0, 1, 0, 0],
                    [np.sin(r), 0, np.cos(r), 0],
                    [0, 0, 0, 1]
                ], dtype=np.float64
            ))
            geometry.apply_transform(trans)
        # imgui.text("Changed: %s, Values: %s" % (changed, value))

        changed, self.y_rotation_value = imgui.slider_float(
        "Y rotation", self.y_rotation_value,
        min_value=-360, max_value=360.0,
        format="%.0f",
        power=0.5
        )
        self.ignore_clicks = self.ignore_clicks or imgui.is_item_active()

    

        changed, self.z_rotation_value = imgui.slider_float(
        "Z rotation", self.z_rotation_value,
        min_value=-360, max_value=360.0,
        format="%.0f",
        power=0.5
        )
        self.ignore_clicks = self.ignore_clicks or imgui.is_item_active()
        # imgui.end_child()

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
                    box = trimesh.creation.box()
                    box.vertices, box.faces = trimesh.remesh.subdivide_to_size(
                        box.vertices, box.faces, 0.1)

                    scene.add_geometry(box)
                    self.window.reset_view()
                clicked, selected = imgui.menu_item("Sphere")
                if clicked:
                    scene.geometry.popitem()
                    sphere = trimesh.creation.uv_sphere()
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

        imgui.text("Welcome to 3D Sculpting!")
        imgui.text("To beign, select a shape from the 'Primitives' menu above")
        imgui.text("After selecting a shape, you can use either your hands or the mouse to shape the object and control the view")
        

        imgui.end()
        
       
        # imgui.begin("Scale")
        # # changed, values = imgui.input_float4('Type here:', *values)
        # # imgui.text("Changed: %s, Values: %s" % (changed, values))
        # # changed, float_val = imgui.input_float('X', self.scale_x_val)
        # # changed, float_val = imgui.input_float('Y', self.scale_y_val)
        # # changed, float_val = imgui.input_float('Z', self.scale_z_val)
        # # self.window.scale(flo, self.scale_y_val, self.scale_z_val)
        # imgui.end()

        
        imgui.end_frame()
        

        if self.window.state.internal_state['wireframe']:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)


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
          If passed apply keys to self.state.view:
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
        self.selected_vertices_original_ccords = None
        self.selected_vertex_z = None
        
        # select mode is either vertex / sphere
        self.select_mode = 'vertex'
        self.selected_vertices = None

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
        self.gl = GlManager(scene, self.line_settings)

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
        # self.init_gl()
        self.gl.reset_gl()
        self.set_size(*resolution)
        if flags is not None:
            self.reset_view(flags=flags)
        self.update_flags()

        # self.set_mouse_cursor(

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

    def set_mouse_brush_sphere(self, iter):
        # if iter==5:
        #     image = pyglet.image.load('5_iterations_brush.png')
        # if iter==3:
        #     image = pyglet.image.load('3_iterations_brush.png')
        # if iter==1:
        #     image = pyglet.image.load('1_iterations_brush.png')

        # cursor = pyglet.window.ImageMouseCursor(image, 8, 8)
        # self.set_mouse_cursor(cursor)
        self.select_mode = 'sphere'

    def set_defult_mouse_cursor(self):
        default_cursor = pyglet.window.DefaultMouseCursor()
        self.set_mouse_cursor(default_cursor)
        self.select_mode = 'vertex'

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
        self.gl.set_modelview_matrix(self.width, self.height)

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
        self.state = StateManager(self.scene)
        try:
            # if any flags are passed override defaults
            if isinstance(flags, dict):
                for k, v in flags.items():
                    if k in self.state.internal_state:
                        self.state.internal_state[k] = v
                self.update_flags()
        except BaseException:
            pass

    def toggle_wireframe(self):
        """
        Toggle wireframe mode

        Good for  looking inside meshes, off by default.
        """
        self.state.internal_state['wireframe'] = not self.state.internal_state['wireframe']
        self.update_flags()

    def toggle_axis(self):
        """
        Toggle a rendered XYZ/RGB axis marker:
        off, world frame, every frame
        """
        # cycle through three axis states
        states = [False, 'world', 'all', 'without_world']
        # the state after toggling
        index = (states.index(self.state.internal_state['axis']) + 1) % len(states)
        # update state to next index
        self.state.internal_state['axis'] = states[index]
        # perform gl actions
        self.update_flags()

    def toggle_grid(self):
        """
        Toggle a rendered grid.
        """
        # update state to next index
        self.state.internal_state['grid'] = not self.state.internal_state['grid']
        # perform gl actions
        self.update_flags()

    def draw_mouse_cursor(self):
        self.switch_to()
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
        super().draw_mouse_cursor()


    def update_flags(self):
        """
        Check the view flags, and call required GL functions.
        """
        # view mode, filled vs wirefrom
        gl.glEnable(gl.GL_CULL_FACE)

    def on_resize(self, width, height):
        """
        Handle resized windows.
        """
        width, height = self.gl.set_modelview_matrix(width, height)
        self.scene.camera.resolution = (width, height)
        self.state.internal_state['ball'].resize(self.scene.camera.resolution)
        self.scene.camera_transform[...] = self.state.internal_state['ball'].pose

    def on_mouse_press(self, x, y, buttons, modifiers):
        """
        Set the start point of the drag.
        """
        self.switch_to()
        self.state.internal_state['ball'].set_state(Trackball.STATE_ROTATE)
        if (buttons == pyglet.window.mouse.LEFT):
            ctrl = (modifiers & pyglet.window.key.MOD_CTRL)
            shift = (modifiers & pyglet.window.key.MOD_SHIFT)
            alt = (modifiers & pyglet.window.key.MOD_ALT)
            if alt:
                scene: Scene = self.scene
                self.geom_copy = scene.geometry['geometry_0'].copy()
                if self.select_mode == 'vertex':
                    print("mouse_press before select vertex")
                    self.select_vertex()
                    print("mouse_press after select vertex")
                else:
                    self.collide_with_sphere()
            elif (ctrl and shift):
                self.state.internal_state['ball'].set_state(Trackball.STATE_ZOOM)
            elif shift:
                self.state.internal_state['ball'].set_state(Trackball.STATE_ROLL)
            elif ctrl:
                self.state.internal_state['ball'].set_state(Trackball.STATE_PAN)
        elif (buttons == pyglet.window.mouse.MIDDLE):
            self.state.internal_state['ball'].set_state(Trackball.STATE_PAN)
        elif (buttons == pyglet.window.mouse.RIGHT):
            self.state.internal_state['ball'].set_state(Trackball.STATE_ZOOM)

        self.state.internal_state['ball'].down(np.array([x, y]))
        
        
        self.scene.camera_transform[...] = self.state.internal_state['ball'].pose

        print("finish mouse_press func")    

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """
        Pan or rotate the view.
        """
        self.switch_to()
        if self.ui.ignore_clicks:
            return
        alt = (modifiers & pyglet.window.key.MOD_ALT)
        if alt:
            if self.selected_vertices is not None:
                self.drag_vertex()
        else:
            try:
                self.state.internal_state['ball'].drag(np.array([x, y]))
                self.scene.camera_transform[...] = self.state.internal_state['ball'].pose
            except:
                pass

    def on_mouse_scroll(self, x, y, dx, dy):
        """
        Zoom the view.fh
        """
        self.state.internal_state['ball'].scroll(dy)
        self.scene.camera_transform[...] = self.state.internal_state['ball'].pose

    def on_mouse_release(self, x, y, button, modifiers):
        self.selected_vertices = None

    def on_key_press(self, symbol, modifiers):
        """
        Call appropriate functions given key presses.
        """
        magnitude = 10
        if symbol == pyglet.window.key.W:
            self.toggle_wireframe()
        elif symbol == pyglet.window.key.Z:
            self.reset_view()
        elif symbol == pyglet.window.key.A:
            self.toggle_axis()
        elif symbol == pyglet.window.key.G:
            self.toggle_grid()
        elif symbol == pyglet.window.key.Q:
            self.on_close()
        elif symbol == pyglet.window.key.M:
            self.maximize()
        elif symbol == pyglet.window.key.S:
            self.select_vertex()
        elif symbol == pyglet.window.key.L:
            self.drag_vertex()
        elif symbol == pyglet.window.key.P:
            self.collide_with_sphere()
        elif symbol == pyglet.window.key.I:
            self.scale()
        elif symbol == pyglet.window.key.ESCAPE:
            self.set_defult_mouse_cursor()
        
        if symbol in [
                pyglet.window.key.LEFT,
                pyglet.window.key.RIGHT,
                pyglet.window.key.DOWN,
                pyglet.window.key.UP]:
            self.state.internal_state['ball'].down([0, 0])
            if symbol == pyglet.window.key.LEFT:
                self.state.internal_state['ball'].drag([-magnitude, 0])
            elif symbol == pyglet.window.key.RIGHT:
                self.state.internal_state['ball'].drag([magnitude, 0])
            elif symbol == pyglet.window.key.DOWN:
                self.state.internal_state['ball'].drag([0, -magnitude])
            elif symbol == pyglet.window.key.UP:
                self.state.internal_state['ball'].drag([0, magnitude])
            self.scene.camera_transform[...] = self.state.internal_state['ball'].pose

    def scale(self, x, y, z):
        scene: Scene = self.scene
        geom: Trimesh = scene.geometry.get('geometry_0')
        geom.apply_scale([x, y, z])

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

        self.switch_to()
        if self.state.internal_state['wireframe']:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        # else:
        #     gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)


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
        if self._axis and not self.state.internal_state['axis'] == 'without_world':
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
            if self.state.internal_state['axis'] == 'all':
                self._axis.draw(mode=gl.GL_TRIANGLES)
            elif self.state.internal_state['axis'] == 'without_world':
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

        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
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

        # z0 = (GLfloat * 1)()
        z0 = glReadPixels(x, y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)

        return z0

    def select_vertex(self):
        print("start func select vertex")
        x, y = self.get_mouse_coords()
        z = self.get_z_for_coord(x, y)
        print("select vertex before glu")
        # convert pixel to world coordinates, if data is not empty, you will see 'normal' values (small sizes)
        coord = gluUnProject(x, y, z)
        print("select vertex after glu")

        scene: Scene = self.scene
        geom: Trimesh = scene.geometry.get('geometry_0')
        # find distance and index of closest vertex to mouse coordinates
        dist, index = scipy.spatial.KDTree(geom.vertices).query(coord)
        print(dist)
        threshold = 0.1 if not self.state.internal_state['wireframe'] else 0.3
        if dist < threshold:
            self.selected_vertices = [index]
            self.selected_vertex_z = z
            self.selected_vertices_original_ccords = [coord]
        else:
            self.selected_vertices = None
            self.selected_vertex_z = None
            self.selected_vertices_original_ccords = None
            
        print("endof func select vertex")
        print(f"Selecting vertex: {self.selected_vertices}")

    def extend_vertex_selection(self, vertex_list, iterations=5):
        scene: Scene = self.scene
        geom: Trimesh = scene.geometry['geometry_0']
        faces = geom.faces
        selected_vertices = [*vertex_list]
        for i in range(iterations):
            mask = np.maximum.reduce(np.isin(faces, selected_vertices), axis=1)
            selected_vertices = np.unique(faces[mask].flatten())

        return selected_vertices

    def smooth(self, vertices):
        scene: Scene = self.scene
        geom: Trimesh = scene.geometry['geometry_0']
        all_vertices = np.arange(len(geom.vertices))
        pinned = np.delete(all_vertices, vertices)

        operator = trimesh.smoothing.laplacian_calculation(
            geom, pinned_vertices=pinned)
        trimesh.smoothing.filter_taubin(geom, laplacian_operator=operator)

    def drag_vertex(self):
        print("start drag")
        if self.selected_vertices is None:
            print("no selected vertex")
            return
        scene: Scene = self.scene
        geom: Trimesh = scene.geometry.get('geometry_0')
        # geom.vertices = self.geom_copy.vertices.copy()
        x, y = self.get_mouse_coords()
        # z = self.get_z_for_coord(x, y)
        print("drag vertex before glu")
        coords = gluUnProject(x, y, self.selected_vertex_z)
        print("drag vertex after glu")
        if coords[0] > 100 or coords[1] > 100 or coords[2] > 100:
            print ("after line 1210")
            return
        # print(coords)
        vertices_copy = deepcopy(self.selected_vertices_original_ccords)
        for idx, v in zip(self.selected_vertices, vertices_copy):
            dir = np.array(coords) - np.array(v)
            geom.vertices[idx] = dir + v

        # trimesh.smoothing.filter_taubin(geom)
        self.smooth(self.extend_vertex_selection(self.selected_vertices))
        print("endof drag vertex")

    def collide_with_sphere(self):
        x, y = self.get_mouse_coords()
        z = self.get_z_for_coord(x, y)
        cx, cy, cz = gluUnProject(x, y, z)
        sphere = trimesh.primitives.Sphere(center=[cx, cy, cz], radius=0.1)
        scene: Scene = self.scene
        geom: Trimesh = scene.geometry['geometry_0']
        mask = sphere.contains(geom.vertices)
        print(mask, "hello")
        vertices = []
        for i, m in enumerate(mask):
            if m:
                vertices.append(i)

        self.selected_vertices = vertices
        self.selected_vertices_original_ccords = [geom.vertices[idx].copy() for idx in vertices]
        self.selected_vertex_z = cz
        # self.smooth(self.extend_vertex_selection(vertices))


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
    init_camera_window(viewer)
    # handgest=Hand_handler(viewer)
    pyglet.app.run()  # blocking!!!!!!!!!


if __name__ == '__main__':
    # import trace
    # tracer = trace.Trace(
    #     ignoredirs=[sys.prefix, sys.exec_prefix, '/home/moriel99/.local/lib/python3.9/'],
    # )
    # tracer.run('init_3d()')
    # r = tracer.results()
    # r.write_results(show_missing=True, coverdir=".")

    init_3d()
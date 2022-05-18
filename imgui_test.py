import sys
import threading
import multiprocessing
import collections
from graphviz import view
from matplotlib.pyplot import sca
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
pyglet.options['shadow_window'] = True
import pyglet.gl as gl  # NOQA



class UI:
    def __init__(self, window):
        imgui.create_context()
        self.renderer = PygletRenderer(window)
        self.impl = PygletRenderer(window)
        imgui.new_frame()
        imgui.end_frame()

        # Window variables

        # self.window: SceneViewer = window
        self.test_input = 0

    def render(self):
        imgui.render()
        io = imgui.get_io()
        self.impl.render(imgui.get_draw_data())
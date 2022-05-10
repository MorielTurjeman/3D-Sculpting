from ..trimesh_test import *
import pyglet
camera_size = (960, 540)
screen_size = (1920, 1080)





def hand_gesture_to_action(hand_gesture):
    if hand_gesture == 'Scale_IN':
        print("Scale_IN")
    if hand_gesture == 'Scale_OUT':
        print("Scale_OUT")
    if hand_gesture == 'Rotate_LEFT':
        print('Rotate_LEFT')
    if hand_gesture == 'Rotate_RIGHT':
        print('Rotate_RIGHT')
    if hand_gesture == 'Rotate_UP':
        print('Rotate_UP')
    if hand_gesture == 'Rotate_DOWN':
        print('Rotate_DOWN')
    if hand_gesture == 'Rotate_Z_AXIS':
        print('Rotate_Z_AXIS')
    if hand_gesture == 'Stretch':
        print('Stretch')
    if hand_gesture == 'Shrink':
        print('Shrink')


class Hand_handler:
    def __init__(self, scene_viewer):
        self.SceneViewer = scene_viewer
        self.state = "None"

    def rotate(self,state,  x=0, y=0):
        x_ = int(x / camera_size[0] * screen_size[0])
        y_ = int(y / camera_size[1] * screen_size[1])

        if self.state != state: #first time in state
            self.UI.on_mouse_press(x_, y_, pyglet.window.mouse.LEFT, None)
            self.state = state
        else:
            self.UI.on_mouse_drag(x_, y_, None, None, pyglet.window.mouse.LEFT, None)


    def scale(self ,state,  x=0, y=0):
        x_ = int(x / camera_size[0] * screen_size[0])
        y_ = int(y / camera_size[1] * screen_size[1])

        if self.state != state: #first time in state
            self.UI.on_mouse_press(x_, y_, pyglet.window.mouse.LEFT, None)
            self.state = state
        else:
            #self.UI.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
            print("rotate")

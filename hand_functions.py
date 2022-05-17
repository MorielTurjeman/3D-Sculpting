# from ..trimesh_test import *
from pickletools import pyfloat
import pyglet
camera_size = (960, 540)
screen_size = (1920, 1080)

last_gesture = None

def hand_gesture_to_action(hand_gesture,landmark_middel_tip, mouse_press, mouse_move, mouse_scroll):
    # hand_hendler = Hand_handler()
    global last_gesture    
    if hand_gesture == 'Scale_IN': # change to zoom in
        if last_gesture != hand_gesture:
            last_gesture = hand_gesture
            mouse_scroll(0,0,0,1)
        else:
            mouse_scroll(0,0,0,1)
            print("Scale_IN",landmark_middel_tip)

    if hand_gesture == 'Scale_OUT': #change to zoom out
        if last_gesture != hand_gesture:
            last_gesture = hand_gesture
            mouse_scroll(0,0,0,-1)
        else:
            print("Scale_OUT",landmark_middel_tip)
            mouse_scroll(0,0,0,-1)
            
    if hand_gesture == 'Rotate_LEFT':
        if last_gesture != hand_gesture:
            last_gesture = hand_gesture
            mouse_press(*landmark_middel_tip, pyglet.window.mouse.LEFT, 0)
        else:
            mouse_move(*landmark_middel_tip, 0, 0, 0, 0)
            print('Rotate_LEFT',landmark_middel_tip)
            
        # hand_hendler.rotate( state = 'Rotate_LEFT', x=landmark_middel_tip[0], y=landmark_middel_tip[1])
    if hand_gesture == 'Rotate_RIGHT':
        if last_gesture != hand_gesture:
            last_gesture = hand_gesture
        else:
            print('Rotate_RIGHT')
    if hand_gesture == 'Rotate_UP':
        if last_gesture != hand_gesture:
            last_gesture = hand_gesture
        else:
            print('Rotate_UP')
    if hand_gesture == 'Rotate_DOWN':
        if last_gesture != hand_gesture:
            last_gesture = hand_gesture
        else:
            print('Rotate_DOWN')
    if hand_gesture == 'Rotate_Z_AXIS':
        if last_gesture != hand_gesture:
            last_gesture = hand_gesture
        else:
            print('Rotate_Z_AXIS')
    if hand_gesture == 'Stretch':
        if last_gesture != hand_gesture:
            last_gesture = hand_gesture
        else:
            print('Stretch')
    if hand_gesture == 'Shrink':
        if last_gesture != hand_gesture:
            last_gesture = hand_gesture
        else:
            print('Shrink')



# class Hand_handler:
#     def __init__(self):
#         self.scene_viewer =
#         self.state = "None"
#
#     def rotate(self,state,  x=0, y=0):
#         x_ = int(x / camera_size[0] * screen_size[0])
#         y_ = int(y / camera_size[1] * screen_size[1])
#
#         if self.state != state: #first time in state
#             self.scene_viewer.on_mouse_press(x_, y_, pyglet.window.mouse.LEFT, None)
#             self.state = state
#         else:
#             self.scene_viewer.on_mouse_drag(x_, y_, None, None, pyglet.window.mouse.LEFT, None)
#
#
#     def scale(self ,state,  x=0, y=0):
#         x_ = int(x / camera_size[0] * screen_size[0])
#         y_ = int(y / camera_size[1] * screen_size[1])
#
#         if self.state != state: #first time in state
#             self.scene_viewer.on_mouse_press(x_, y_, pyglet.window.mouse.LEFT, None)
#             self.state = state
#         else:
#             #self.UI.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
#             print("rotate")

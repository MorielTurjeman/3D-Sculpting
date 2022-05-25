# from ..trimesh_test import *
from pickletools import pyfloat
import pyglet
import numpy as np
camera_size = (960, 540)
screen_size = (1920, 1080)
last_scale = None
last_gesture = None
lastdy=0

def hand_gesture_multi_hand(left_gesture, right_gesture, left_landmark, right_landmark, ymax, xmax, depth, viewer):
    global last_gesture
    global lastdy
    global last_scale
    
    if right_gesture is None:
        hand_gesture_to_action(left_gesture, viewer, left_landmark, ymax, xmax, depth)
    elif left_gesture is None:
        hand_gesture_to_action(right_gesture, viewer, right_landmark, ymax, xmax, depth)
    else:
        if ((left_gesture == 'Stop' or left_gesture == 'Rotate')
            and (right_gesture == 'Stop' or right_gesture == 'Rotate')):
            # this is actually a scale gesture
            left_coord = np.array(left_landmark[9])
            right_coord = np.array(right_landmark[9])
            scale = np.abs(left_coord, right_coord)
            if last_gesture != 'Scale':
                last_scale = scale
                last_gesture = 'Scale'
            else:
                diff = last_scale / scale
                print(diff)
                viewer.scale(diff[0], diff[1], 1)
            last_scale = scale
        else:
            print("Multihand development")

def hand_gesture_to_action(hand_gesture,viewer, landmark_list, ymax, xmax, depth):
    # hand_hendler = Hand_handler()
    global last_gesture
    global lastdy
    viewer.set_defult_mouse_cursor()
    if hand_gesture == 'Zoom':
        dy = landmark_list[8][1] - landmark_list[4][1]
        if last_gesture != hand_gesture:
            lastdy = dy
            last_gesture = hand_gesture
        else:
            diff = lastdy - dy
            if abs(diff) > 3:
                viewer.on_mouse_scroll(0,0,0, 1 if diff > 0 else -1)
                lastdy = dy
    elif hand_gesture == 'Rotate':
        last_coord = landmark_list[9]
        last_coord[1] = ymax - last_coord[1]
        if last_gesture != hand_gesture:
            last_gesture = hand_gesture
            viewer.on_mouse_press(last_coord[0], last_coord[1], pyglet.window.mouse.LEFT, 0)
        else:
            viewer.on_mouse_drag(last_coord[0], last_coord[1], 0, 0, pyglet.window.mouse.LEFT, 0)
    elif hand_gesture == 'Rotate_Z':
        last_coord = landmark_list[9]
        last_coord[1] = ymax - last_coord[1]
        if last_gesture != hand_gesture:
            last_gesture = hand_gesture
            viewer.on_mouse_press(last_coord[0], last_coord[1], pyglet.window.mouse.LEFT, pyglet.window.key.MOD_SHIFT)
        else:
            viewer.on_mouse_drag(last_coord[0], last_coord[1], 0, 0, pyglet.window.mouse.LEFT, 0)
    # elif hand_gesture == 'Push':
    #     viewer.set_mouse_brush_sphere()
    #     viewer.set_mouse_position(*landmark_list[9])
    else:
        print(hand_gesture)
        
    # if hand_gesture == 'Scale_OUT': #change to zoom out
    #     if last_gesture != hand_gesture:
    #         last_gesture = hand_gesture
    #         mouse_scroll(0,0,0,-1)
    #     else:
    #         print("Scale_OUT",landmark_middel_tip)
    #         mouse_scroll(0,0,0,-1)
            
    # if hand_gesture == 'Rotate_LEFT':
    #     if last_gesture != hand_gesture:
    #         last_gesture = hand_gesture
    #         mouse_press(*landmark_middel_tip, pyglet.window.mouse.LEFT, 0)
    #     else:
    #         mouse_move(*landmark_middel_tip, 0, 0, 0, 0)
    #         print('Rotate_LEFT',landmark_middel_tip)
            
    #     # hand_hendler.rotate( state = 'Rotate_LEFT', x=landmark_middel_tip[0], y=landmark_middel_tip[1])
    # if hand_gesture == 'Rotate_RIGHT':
    #     if last_gesture != hand_gesture:
    #         last_gesture = hand_gesture
    #     else:
    #         print('Rotate_RIGHT')
    # if hand_gesture == 'Rotate_UP':
    #     if last_gesture != hand_gesture:
    #         last_gesture = hand_gesture
    #     else:
    #         print('Rotate_UP')
    # if hand_gesture == 'Rotate_DOWN':
    #     if last_gesture != hand_gesture:
    #         last_gesture = hand_gesture
    #     else:
    #         print('Rotate_DOWN')
    # if hand_gesture == 'Rotate_Z_AXIS':
    #     if last_gesture != hand_gesture:
    #         last_gesture = hand_gesture
    #     else:
    #         print('Rotate_Z_AXIS')
    # if hand_gesture == 'Stretch':
    #     if last_gesture != hand_gesture:
    #         last_gesture = hand_gesture
    #     else:
    #         print('Stretch')
    # if hand_gesture == 'Shrink':
    #     if last_gesture != hand_gesture:
    #         last_gesture = hand_gesture
    #     else:
    #         print('Shrink')
    


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

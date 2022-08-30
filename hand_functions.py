# from ..trimesh_test import *
from pickletools import pyfloat
from graphviz import view
import pyglet
import numpy as np
camera_size = (960, 540)
screen_size = (1920, 1080)
last_scale = None
last_gesture = None
lastdy=0
selected_vertex_original_coord = None


def hand_gesture_multi_hand(left_gesture, right_gesture, left_landmark, right_landmark, ymax, xmax, depth, viewer):
    global last_gesture
    global lastdy
    global last_scale
    global selected_vertex_original_coord

    if right_gesture is None:
        hande_gesture_single_hand(left_gesture, viewer, left_landmark, ymax, xmax, depth)
    elif left_gesture is None:
        hande_gesture_single_hand(right_gesture, viewer, right_landmark, ymax, xmax, depth)
    else:
        if ((left_gesture == 'Stop' or left_gesture == 'Rotate')
            and (right_gesture == 'Stop' or right_gesture == 'Rotate')):
            # this is actually a scale gesture
            left_coords = np.array(left_landmark[9])
            right_coords = np.array(right_landmark[9])
            scale = np.abs(left_coords, right_coords)
            if last_gesture != 'Scale':
                last_scale = scale
                last_gesture = 'Scale'
            else:
                diff = last_scale / scale
                viewer.scale(diff[0], diff[1], 1)
            last_scale = scale
        elif left_gesture == 'Pull' and right_gesture == 'Pull':
            # this is actually move vertex
            left_coords = np.array([left_landmark[4][0], ymax - left_landmark[4][1]])
            right_coords = np.array([right_landmark[4][0], ymax - right_landmark[4][1]])

            left_norm = normalize_coords(*left_coords, xmax, ymax, viewer)
            right_norm = normalize_coords(*right_coords, xmax, ymax, viewer)
            mouse_pos = np.array(selected_vertex_original_coord)

            dist_left = np.linalg.norm(left_norm - mouse_pos)
            dist_right = np.linalg.norm(right_norm - mouse_pos)

            target_coord = left_norm if dist_left > dist_right else right_norm
            try:
                viewer.set_mouse_position(*target_coord)
                viewer.on_mouse_drag(*target_coord, 0, 0, pyglet.window.mouse.LEFT, pyglet.window.key.MOD_ALT)
            except:
                pass
        else:
            print("Multihand development")

def normalize_coords(x, y, xmax, ymax, viewer):
    wx, wy = viewer.get_viewport_size()
    x = int(x / xmax * wx)
    y = int(y / ymax * wy)
    return x, y
    

def hande_gesture_single_hand(hand_gesture,viewer: pyglet.window.Window, landmark_list, ymax, xmax, depth):
    # hand_hendler = Hand_handler()
    global last_gesture
    global lastdy
    global selected_vertex_original_coord
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
    elif hand_gesture == 'Rotate' or hand_gesture=='Stop':
        last_coord = landmark_list[9]
        last_coord[1] = ymax - last_coord[1]
        if last_gesture != hand_gesture:
            last_gesture = hand_gesture
            viewer.on_mouse_press(last_coord[0], last_coord[1], pyglet.window.mouse.LEFT, 0)
        else:
            viewer.on_mouse_drag(last_coord[0], last_coord[1], 0, 0, pyglet.window.mouse.LEFT, 0)
    elif hand_gesture == 'Rotate_Z' or hand_gesture=='Stop':
        last_coord = landmark_list[9]
        last_coord[1] = ymax - last_coord[1]
        if last_gesture != hand_gesture:
            last_gesture = hand_gesture
            viewer.on_mouse_press(last_coord[0], last_coord[1], pyglet.window.mouse.LEFT, pyglet.window.key.MOD_SHIFT)
        else:
            viewer.on_mouse_drag(last_coord[0], last_coord[1], 0, 0, pyglet.window.mouse.LEFT, 0)
    elif hand_gesture == "Pull":
        try:
            coord = [landmark_list[4][0], ymax - landmark_list[4][1]]
            coord = normalize_coords(*coord, xmax, ymax, viewer)
            viewer.set_mouse_position(*coord)
            viewer.on_mouse_press(*coord, pyglet.window.mouse.LEFT, pyglet.window.key.MOD_ALT)
            last_gesture = 'Pull'
            selected_vertex_original_coord = coord
        except:
            pass
    elif hand_gesture == 'Choose':
        try:
            coord = landmark_list[8]
            coord = normalize_coords(*coord, xmax, ymax, viewer)
            viewer.on_mouse_press(*coord, pyglet.window.mouse.LEFT, 0)
        except:
            pass
    else:
        print(hand_gesture)
        
    
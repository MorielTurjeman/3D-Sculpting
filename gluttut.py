import sys
import numpy as np
from OpenGL import GLUT, GL
from cube import Cube, Model
from glsl_program import GLSLProgram
from mouse_picker import MouseHandler
from projection import Projection
from texture import Texture
from world import World
from camera import Camera
from framebuffer import Framebuffer
from functools import partial

camera = None
framebuffer: Framebuffer = None
mouse_picker: MouseHandler = None
cube: Model = None
last_mouse_click = None
selected_vertex = None
mouse_mode = False
world: World = None


def render_scene_cb():
    global framebuffer
    global mouse_picker
    # picking
    mouse_picker.enable_writing()
    framebuffer.picking_render(mouse_picker.texture)
    mouse_picker.disable_writing()
    # picking done
    framebuffer.render()
    GLUT.glutPostRedisplay()
    GLUT.glutSwapBuffers()


def compile_shaders(glsl_program: GLSLProgram):
    glsl_program.add_shader_codlet(framebuffer)
    glsl_program.compile_and_use_program()


def update_model_vertex(vertex_id: int):
    global cube
    cube.set_vertex(vertex_id, 0.8, 0.8, -0.5)
    framebuffer.write_buffers()
    return


def mouse_handler(button, state, x, y):
    global mouse_picker
    global last_mouse_click
    global framebuffer
    global selected_vertex
    global mouse_mode
    height = GLUT.glutGet(GLUT.GLUT_WINDOW_HEIGHT)
    width = GLUT.glutGet(GLUT.GLUT_WINDOW_WIDTH)
    screen_coord = [x, height - y - 1]

    if (button == GLUT.GLUT_LEFT_BUTTON and state == GLUT.GLUT_DOWN):
        # Y coordinates are inversed in opengl,
        # so inverse the y coord of the mouse click
        mouse_mode = 'Dragging'
        vertex_id = mouse_picker.handle_mouse(*screen_coord)
        if (vertex_id > 0):
            selected_vertex = vertex_id
            last_mouse_click = framebuffer.get_model_coord(screen_coord)
            if last_mouse_click is not None:
                mouse_mode = 'Dragging'
                print(f"origin: {last_mouse_click}")
            # update_model_vertex(vertex_id)
    elif (button == GLUT.GLUT_LEFT_BUTTON and state == GLUT.GLUT_UP):
        selected_vertex = None
        last_mouse_click = None
    elif button == GLUT.GLUT_RIGHT_BUTTON or button == GLUT.GLUT_MIDDLE_BUTTON:
        if state == GLUT.GLUT_DOWN:
            if last_mouse_click is None:
                last_mouse_click = np.array(screen_coord, dtype=np.float32)
                mouse_mode = World.ROTATE_YZ if button == GLUT.GLUT_RIGHT_BUTTON else World.ROTATE_XZ
        if state == GLUT.GLUT_UP:
            last_mouse_click = None
    elif button is None and state == "Motion":
        if mouse_mode == 'Dragging' and selected_vertex:
            curr_mouse_click = framebuffer.get_model_coord(screen_coord)
            delta = curr_mouse_click - last_mouse_click
            last_mouse_click = curr_mouse_click
            cube.move_vertex_in_vector(selected_vertex, *delta[:3])
            framebuffer.write_buffers()
        elif mouse_mode == World.ROTATE_YZ:
            curr_mouse_click = np.array(screen_coord, dtype=np.float32)
            delta = (curr_mouse_click[0] - last_mouse_click[0]) / width
            world.set_rotation(delta, world.ROTATE_YZ)
        elif mouse_mode == world.ROTATE_XZ:
            curr_mouse_click = np.array(screen_coord, dtype=np.float32)
            delta = (curr_mouse_click[1] - last_mouse_click[1]) / height
            world.set_rotation(delta, world.ROTATE_XZ)

            # delta = (curr_mouse_click[1] - last_mouse_click[1]) / height
            # world.set_rotation(delta, World.ROTATE_XZ)


def main():
    global framebuffer
    global mouse_picker
    global cube
    global world

    GLUT.glutInit(sys.argv)
    GLUT.glutInitDisplayMode(
        GLUT.GLUT_DOUBLE |
        GLUT.GLUT_RGBA |
        GLUT.GLUT_3_2_CORE_PROFILE |
        GLUT.GLUT_FORWARD_COMPATIBLE
    )
    GLUT.glutInitWindowSize(800, 800)
    GLUT.glutInitWindowPosition(100, 100)
    GLUT.glutCreateWindow("Tutorial")

    world = World()
    projection = Projection()
    camera = Camera()
    world.set_position(0, 0, 3)

    texture = Texture('./bricks.jpeg', GL.GL_TEXTURE_2D)
    if not texture.load():
        raise ValueError("Could not load texture")
    print("here")

    GL.glPointSize(15)

    framebuffer = Framebuffer(world, projection, camera, texture)

    mouse_picker = MouseHandler()

    cube = Cube()
    framebuffer.add_model(cube)
    framebuffer.write_buffers()
    framebuffer.compile_shaders()
    GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
    GL.glClearColor(0, 0, 0, 0)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT)
    GL.glEnable(GL.GL_CULL_FACE)
    GL.glFrontFace(GL.GL_CW)
    GL.glCullFace(GL.GL_BACK)

    GLUT.glutDisplayFunc(render_scene_cb)
    GLUT.glutIdleFunc(render_scene_cb)
    GLUT.glutSpecialFunc(camera.handle_keyboard)
    GLUT.glutMotionFunc(partial(mouse_handler, None, "Motion"))
    GLUT.glutMouseFunc(mouse_handler)

    GLUT.glutMainLoop()


if __name__ == '__main__':
    main()

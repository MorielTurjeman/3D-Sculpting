from trimesh import Scene
from trimesh.viewer.trackball import Trackball

class StateManager:
    def __init__(self, scene: Scene):
        self.scene = scene
        self._initial_camera_transform = scene.camera_transform.copy()
        self.internal_state = {
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
       
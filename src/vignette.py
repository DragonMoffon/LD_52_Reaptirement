from typing import Tuple

from arcade import Sprite

from src.data import WindowData


def set_vignette():
    WindowData.set_vignette(Vignette())


class Vignette(Sprite):

    def __init__(self):
        super().__init__(":assets:/textures/vignette.png")
        self.position = WindowData.down_scale_resolution[0]//2, WindowData.down_scale_resolution[1]//2
        self.visible = False

    def show_vignette(self, colour: Tuple[float, float, float, float]):
        self.color = colour[0] * 255, colour[1] * 255, colour[2] * 255
        self.alpha = colour[-1] * 255 * 0.1
        self.visible = True

    def hide_vignette(self):
        self.color = 0, 0, 0
        self.alpha = 0
        self.visible = False

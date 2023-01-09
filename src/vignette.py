from typing import Tuple

from arcade import Sprite

from src.data import WindowData


def set_vignette():
    WindowData.set_vignette(Vignette())


class Vignette(Sprite):

    def __init__(self):
        super().__init__(":assets:/textures/vignette.png")
        self.position = WindowData.down_scale_resolution[0]//2, WindowData.down_scale_resolution[1]//2
        self.hide_vignette()

    def show_vignette(self, colour: Tuple[int, int, int]):
        self.color = colour
        self.alpha = 25
        self.visible = True

    def hide_vignette(self):
        self.color = 0, 0, 0
        self.alpha = 2
        self.visible = True

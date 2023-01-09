from typing import NamedTuple, Tuple

from arcade import Sprite, Texture

from src.clock import Clock


class AnimationData(NamedTuple):
    frames: Tuple[Texture, ...]
    timings: Tuple[float, ...]
    loop: bool = False


class AnimatedSprite(Sprite):

    def __init__(self, data: AnimationData, position: Tuple[float, float], angle: float = 0.0):
        super().__init__()
        self.angle = angle
        self.data = data
        self.position = position

        self.current_frame = 0
        self.texture = self.data.frames[0]

        self.frame_time: float = Clock.time

    def update_texture(self):
        _t = Clock.length(self.frame_time) / self.data.timings[self.current_frame]
        if _t >= 1.0:
            self.frame_time = Clock.time
            if self.current_frame+1 >= len(self.data.frames) and not self.data.loop:
                return
            self.current_frame = (self.current_frame+1)%len(self.data.frames)
            self.texture = self.data.frames[self.current_frame]

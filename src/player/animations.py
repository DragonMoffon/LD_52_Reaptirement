from typing import Dict, Tuple

from arcade import Texture, load_texture, Sprite


from src.clock import Clock


class PlayerAnimator:
    c_frame_size: Tuple[int, int] = (16, 16)
    c_frame_duration: float = 1/5
    c_animation_data: Dict[str, Dict] = {
        "idle": {'src': ":assets:/textures/player/reaper1.png", 'frames': 6, 'y': 0},
        "walk": {'src': ":assets:/textures/player/reaper1.png", 'frames': 6, 'y': 0}
    }

    def __init__(self, target: Sprite):
        self._target = target

        self._animations: Dict[str, Tuple[Texture, ...]] = dict()
        for name, data in PlayerAnimator.c_animation_data.items():
            _x = 0
            _y = data['y']
            frames = []
            for frame in range(data['frames']):
                _texture = load_texture(data['src'], _x, _y,
                                        width=PlayerAnimator.c_frame_size[0], height=PlayerAnimator.c_frame_size[1])
                _x += PlayerAnimator.c_frame_size[0]
                frames.append(_texture)
            self._animations[name] = tuple(frames)

        self._current_frames: Tuple[Texture, ...] = self._animations["idle"]
        self._current_animation: str = "idle"
        self._next_animation: str = "idle"

        self._current_frame: int = 0
        self._frame_time: float = 0

        target.texture = self._current_frames[0]

    def pend_animation(self, _next: str):
        self._next_animation = _next

    def interrupt_animation(self, _anim: str):
        self._current_animation = _anim
        self._current_frames = self._animations[self._current_animation]

        self._current_frame = 0
        self._frame_time = Clock.time

    def animate(self):
        if Clock.length(self._frame_time) < PlayerAnimator.c_frame_duration:
            return

        self._current_frame += 1
        self._frame_time = Clock.time

        if self._current_frame >= len(self._current_frames):
            self._current_animation = self._next_animation
            self._current_frames = self._animations[self._current_animation]
            self._next_animation = "idle"

            self._current_frame = 0

        self._target.texture = self._current_frames[self._current_frame]





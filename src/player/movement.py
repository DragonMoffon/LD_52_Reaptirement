from typing import List

from arcade import Sprite, lerp
from src.keys import UP, DOWN, LEFT, RIGHT, RSHIFT

from src.clock import Clock

from src.data import PlayerData, WindowData


class Movement:
    c_knockback_decay: float = 0.05

    def __init__(self, source: Sprite):
        self._source = source

        self.horizontal_direction: int = 0
        self.vertical_direction: int = 0

        self.directions: List[bool, bool, bool, bool] = [False, False, False, False]

    def update(self):
        if PlayerData.knockback[0] or PlayerData.knockback[1]:
            _dx = lerp(PlayerData.knockback[0], 0.0, Movement.c_knockback_decay)
            _dy = lerp(PlayerData.knockback[1], 0.0, Movement.c_knockback_decay)

            if abs(_dx) < 0.05:
                _dx = 0.0
            if abs(_dy) < 0.05:
                _dy = 0.0

            PlayerData.knockback = _dx, _dy
            _x = PlayerData.raw_x + _dx * Clock.delta_time
            _y = PlayerData.raw_y + _dy * Clock.delta_time

            PlayerData.raw_pos = (_x, _y)

        if not PlayerData.control:
            return

        self.horizontal_direction = self.directions[0] - self.directions[1]
        self.vertical_direction = self.directions[-1] - self.directions[-2]

        PlayerData.velocity = (self.horizontal_direction * PlayerData.max_speed,
                               self.vertical_direction * PlayerData.max_speed)
        _x = PlayerData.raw_x + PlayerData.velocity[0] * Clock.delta_time
        _y = PlayerData.raw_y + PlayerData.velocity[1] * Clock.delta_time

        _bounds = WindowData.game_view.current_map.bounds

        _x = min(max(_bounds[0], _x), _bounds[2])
        _y = min(max(_bounds[1], _y), _bounds[3])

        PlayerData.raw_pos = (_x, _y)

    def key_press(self, symbol, modifiers):
        if symbol == RIGHT:
            self.directions[0] = True
        elif symbol == LEFT:
            self.directions[1] = True
        elif symbol == UP:
            self.directions[-1] = True
        elif symbol == DOWN:
            self.directions[-2] = True

    def key_release(self, symbol, modifiers):
        if symbol == RIGHT:
            self.directions[0] = False
        elif symbol == LEFT:
            self.directions[1] = False
        elif symbol == UP:
            self.directions[-1] = False
        elif symbol == DOWN:
            self.directions[-2] = False

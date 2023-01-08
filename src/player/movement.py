from typing import List

from arcade import Sprite
from src.keys import UP, DOWN, LEFT, RIGHT, RSHIFT

from src.clock import Clock

from src.player.data import PlayerData


class Movement:

    def __init__(self, source: Sprite):
        self._source = source

        self.horizontal_direction: int = 0
        self.vertical_direction: int = 0

        self.attempt_sprint: bool = False

        self.directions: List[bool, bool, bool, bool] = [False, False, False, False]

    def update(self):
        self.horizontal_direction = self.directions[0] - self.directions[1]
        self.vertical_direction = self.directions[-1] - self.directions[-2]

        PlayerData.velocity = (self.horizontal_direction * PlayerData.max_speed,
                               self.vertical_direction * PlayerData.max_speed)
        _x = PlayerData.raw_x + PlayerData.velocity[0] * Clock.delta_time
        _y = PlayerData.raw_y + PlayerData.velocity[1] * Clock.delta_time

        PlayerData.raw_position = (_x, _y)
        self._source.position = int(_x), int(_y)

        # print(self.horizontal_direction, self.vertical_direction)

    def key_press(self, symbol, modifiers):
        self.attempt_sprint = modifiers & RSHIFT
        if symbol == RIGHT:
            self.directions[0] = True
        elif symbol == LEFT:
            self.directions[1] = True
        elif symbol == UP:
            self.directions[-1] = True
        elif symbol == DOWN:
            self.directions[-2] = True

    def key_release(self, symbol, modifiers):
        self.attempt_sprint = modifiers & RSHIFT
        if symbol == RIGHT:
            self.directions[0] = False
        elif symbol == LEFT:
            self.directions[1] = False
        elif symbol == UP:
            self.directions[-1] = False
        elif symbol == DOWN:
            self.directions[-2] = False

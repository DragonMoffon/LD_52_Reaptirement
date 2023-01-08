from math import cos, sin, radians
from typing import Tuple

from arcade import lerp

from src.player.data import PlayerData

from src.combat.attack import Attack

from src.clock import Clock


class PlayerEventManager:
    c_knockback_decay = 0.05

    def __init__(self):
        self._player_knockback: Tuple[float, float] = (0.0, 0.0)

    def update(self):
        _kb = self._player_knockback
        _kb_x, _kb_y = lerp(_kb[0], 0.0, self.c_knockback_decay), lerp(_kb[1], 0.0, self.c_knockback_decay)

        if abs(_kb_x) < 0.05:
            _kb_x = 0.0

        if abs(_kb_y) < 0.05:
            _kb_y = 0.0

        self._player_knockback = _kb_x, _kb_y
        _dt = Clock.delta_time
        PlayerData.raw_position = PlayerData.raw_position[0] + _kb_x * _dt, PlayerData.raw_position[1] + _kb_y * _dt

    def struck(self, attack: Attack):
        print("ouch!")
        _knockback_power = attack.damage * attack.knockback * 2.0
        if _knockback_power:
            _kb_x = cos(radians(attack.direction)) * _knockback_power
            _kb_y = sin(radians(attack.direction)) * _knockback_power
            self._player_knockback = _kb_x, _kb_y

        PlayerData.take_damage(attack.damage)

    def landed_hit(self, attack: Attack):
        pass

    def use_consumable(self, consumable):
        pass

    def die(self):
        pass

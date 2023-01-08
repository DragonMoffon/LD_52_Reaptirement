from typing import Tuple
from math import atan2, cos, sin, pi, degrees

from arcade import Sprite, SpriteSolidColor, ease_in_out_sin, ease_out, lerp

from src.combat.weapon import Weapon
from src.combat.attack import AttackData, AttackFrame, AttackAnimation, Attack

from src.player.data import PlayerData
from src.data import WindowData

from src.clock import Clock


class Sweep(AttackAnimation):
    c_data: AttackData = AttackData(
        16.0,
        10.0,
        1/60,
        0.0,
        0.0,
        wall_killed=False
    )

    c_start_frame = AttackFrame(0.0, pi/2, 25.0, 1.0)

    def __init__(self, _target):
        super().__init__(_target)
        self._start_time = Clock.time
        self._theta = 0.0

    def _make_attack(self):
        _direction = self._theta
        _hitbox = SpriteSolidColor(32, 32, (255, 255, 255, 255))
        _hitbox.radians = _direction
        _x, _y = self._target[0]+cos(_direction)*45.0, self._target[1]+sin(_direction)*45.0
        _attack = Attack(
            self.c_data,
            (_x, _y),
            degrees(_direction) + 90,
            _hitbox,
            Sprite(":assets:/textures/player/attack_placeholder.png", angle=degrees(_direction) + 90)
        )
        _attack.combat_manager.broadcast_enemy_attack(_attack)

    def animate(self) -> Tuple[float, float, float, Tuple[float, float]]:
        _rotation = 0
        _radius = 45
        _target = self._target

        _t = Clock.length(self._start_time)

        if _t < self.c_start_frame.length:
            _t /= self.c_start_frame.length
            _theta = lerp(self.c_start_frame.theta, 0.0, ease_in_out_sin(_t))
            _radius = lerp(self.c_start_frame.radius, 45.0, ease_in_out_sin(_t))
        else:
            _t -= self.c_start_frame.length
            _theta = pi * _t % (2 * pi)

            self._make_attack()

        self._theta = _theta

        return _rotation, _theta, _radius, _target

    def complete(self) -> bool:
        return Clock.length(self._start_time) >= 24.0


class GeorgieHead(Weapon):

    def __init__(self, _source, _parent_sprite_list):
        _head = Sprite(":assets:/textures/enemies/georgie_placeholder_head.png")
        super().__init__(_source, _head, _parent_sprite_list)

    def update(self):
        if self._stopping_attack:
            _t = Clock.length(self._stopping_attack)
            _rot = lerp(self._rotation, 0.0, ease_out(_t))
            _theta = lerp(self._theta, pi/2, ease_out(_t))
            _radius = lerp(self._radius, 25.0, ease_out(_t))

            if _t >= 1.0:
                self._stopping_attack = 0.0
                self._current_attack = None

        elif self._current_attack:
            _rot, _theta, _radius, _target = self._current_attack.animate()
            self._rotation, self._theta, self._radius = _rot, _theta, _radius
            if self._current_attack.complete():
                self._current_attack = None
        else:
            _rot, _theta, _radius = 0.0, pi/2, 25.0
            self._rotation, self._theta, self._radius = _rot, _theta, _radius
            _target = WindowData.mouse_pos

        _x, _y = self._data.raw_x + cos(_theta) * _radius, self._data.raw_y + sin(_theta) * _radius

        self._sprite.radians = _rot
        self._raw_position = _x, _y
        self._sprite.position = int(_x), int(_y)

    def slam(self):
        if self._current_attack:
            return

    def sweep(self):
        if self._current_attack:
            return

        self._current_attack = Sweep(self._data.raw_pos)



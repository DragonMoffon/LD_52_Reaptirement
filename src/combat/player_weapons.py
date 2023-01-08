from typing import Tuple
from math import atan2, cos, sin, pi, degrees

from arcade import Sprite, SpriteSolidColor, ease_in_out_sin, ease_out, lerp

from src.combat.weapon import Weapon
from src.combat.attack import AttackData, AttackFrame, AttackAnimation, Attack

from src.player.data import PlayerData
from src.data import WindowData

from src.clock import Clock


class PlayerScythe(Weapon):

    def __init__(self, _parent_sprite_list):
        _scythe = Sprite(":assets:/textures/player/Scythe.png")
        super().__init__(_source=PlayerData, _weapon_sprite=_scythe, _parent_sprite_list=_parent_sprite_list)
        self._coins = []

    def update(self):
        if self._current_attack:
            self._rotation, self._theta, self._radius, _target = self._current_attack.animate()
            if self._current_attack.complete():
                self._current_attack = None
        else:
            self._rotation = 0
            self._theta = 0
            self._radius = 6.0

            _target = WindowData.mouse_pos

        _target_dx = self._data.raw_x - _target[0]
        _target_dy = self._data.raw_y - _target[1]
        _theta = atan2(_target_dy, _target_dx)

        _x = self._data.raw_x + cos(_theta + self._theta) * self._radius
        _y = self._data.raw_y + sin(_theta + self._theta) * self._radius

        _rel_x = self._data.raw_x - _x
        _rel_y = self._data.raw_y - _y
        _rotation = atan2(_rel_y, _rel_x)

        self._sprite.radians = _rotation + pi/6 + self._rotation
        self._raw_position = (_x, _y)
        self._sprite.position = int(_x), int(_y)

        for coin in tuple(self._coins):
            coin.animate()
            if coin.landed:
                self._coins.remove(coin)

    def swing(self):
        if self._current_attack:
            return

        _target_dx = WindowData.mouse_pos[0] - self._data.raw_x
        _target_dy = WindowData.mouse_pos[1] - self._data.raw_y
        _dist = (_target_dx ** 2 + _target_dy ** 2) ** 0.5

        for coin in self._coins:
            _dx = coin.position[0] - self._data.raw_x
            _dy = coin.position[1] - self._data.raw_y
            if _target_dx * _dx + _target_dy * _dx >= 0.98 and _dist >= self._data.attack_dist:
                coin.locked = True
                self._current_attack = CatchCoin(coin.position, coin)
                return

        _dist = self._data.attack_dist / _dist
        _target = self._data.raw_x + _target_dx * _dist, self._data.raw_y + _target_dy * _dist
        self._current_attack = Attack1(_target)

    def throw_coin(self):
        if self._current_attack or len(self._coins) >= self._data.max_coins:
            return

        _new_coin = Coin(*self._data.raw_position, *WindowData.mouse_pos)
        self._current_attack = ThrowCoin(WindowData.mouse_pos)
        self._coins.insert(0, _new_coin)
        self._parent_sprite_list.append(_new_coin)


class Attack1(AttackAnimation):
    c_positions: Tuple[AttackFrame, ...] = (  # Rotation, Theta, Radius, length
        AttackFrame(0.0, 0.0, 6.0, 0.05),
        AttackFrame(pi / 4, pi / 4, 12.0, 0.05),
        AttackFrame(pi * 0.8, 1.5 * pi, 14.0, 0.2),
        AttackFrame(pi * 0.75, 1.5 * pi, 14.0, 0.1),
        AttackFrame(pi * 0.1, pi / 6, 9.0, 0.1),
    )
    c_strike_frame: int = 2

    c_attack_data: AttackData = AttackData(
        4.0,
        0.0,
        0.2,
        0.0,
        wall_killed=False
    )

    def __init__(self, _target):
        super().__init__(_target)
        self._frame_start: float = 0.0
        self._current_frame: int = 0

        self._complete = False

    def _make_attack(self):
        _direction = atan2(self._target[1]-PlayerData.raw_y, self._target[0]-PlayerData.raw_x)
        _hitbox = SpriteSolidColor(5, 15, (255, 255, 255))
        _hitbox.radians = _direction
        _attack = Attack(
            self.c_attack_data,
            self._target,
            degrees(_direction),
            _hitbox,
            Sprite(':assets:/textures/player/attack_placeholder.png', angle=degrees(_direction))
        )
        _attack.combat_manager.broadcast_player_attack(_attack)

    def animate(self) -> Tuple[float, float, float, Tuple[float, float]]:
        _frame_values: AttackFrame = self.c_positions[self._current_frame]

        _next_frame = (self._current_frame + 1) % len(self.c_positions)
        _target_values: AttackFrame = self.c_positions[_next_frame]

        _t = Clock.length(self._frame_start) / _frame_values.length

        if _t >= 1.0:
            self._frame_start = Clock.time
            self._current_frame = _next_frame

            if _next_frame == self.c_strike_frame:
                self._attack()

            if _next_frame == 0:
                self._complete = True

        _rotation = lerp(_frame_values.rotation, _target_values.rotation, _t)
        _theta = lerp(_frame_values.theta, _target_values.theta, _t)
        _radius = lerp(_frame_values.radius, _target_values.radius, _t)

        _target = self._target if _next_frame else WindowData.mouse_pos

        return _rotation, _theta, _radius, _target

    def complete(self) -> bool:
        return self._complete


class ThrowCoin(AttackAnimation):
    duration: float = 0.2

    def __init__(self, _target: Tuple[float, float]):
        super().__init__(_target)
        self._start_time = Clock.time

    def animate(self) -> Tuple[float, float, float, Tuple[float, float]]:
        _t = Clock.length(self._start_time) / self.duration
        _rotation = lerp(0, 2.0 * pi, ease_in_out_sin(_t))
        _theta = lerp(0, 2.0 * pi, ease_in_out_sin(_t))
        _radius = 6.0
        _target = self._target
        return _rotation, _theta, _radius, _target

    def complete(self) -> bool:
        return Clock.length(self._start_time) >= self.duration


class Coin(Sprite):
    c_lifespan: float = 0.8

    def __init__(self, x, y, t_x, t_y):
        super().__init__(":assets:/textures/player/coin.png")
        self._spawn_time: float = Clock.time

        self._target_x = t_x
        self._target_y = t_y

        self._start_x = x
        self._start_y = y

        self._raw_position = x, y
        self.position = int(x), int(y)

        self.locked = False
        self.killed = False

    @property
    def landed(self):
        return self.killed or (Clock.length(self._spawn_time) / Coin.c_lifespan >= 1.0 and not self.locked)

    def kill(self) -> None:
        self.remove_from_sprite_lists()
        self.killed = True

    def animate(self):
        if self.locked or self.killed:
            return

        _t = Clock.length(self._spawn_time) / Coin.c_lifespan

        if _t >= 1.0:
            self.remove_from_sprite_lists()
            return

        _x = lerp(self._start_x, self._target_x, ease_out(_t))
        _y = lerp(self._start_y, self._target_y, ease_out(_t))

        self._raw_position = _x, _y
        self.position = int(_x), int(_y)


class CatchCoin(AttackAnimation):
    c_attack_data: AttackData = AttackData(
        8.0,
        0.1,
        2.0,
        160.0,
        0.0,
        30.0
    )

    def __init__(self, _target, _coin: Coin):
        super().__init__(_target)
        self._coin = _coin
        self._start = PlayerData.raw_position

        self._speed = ((self._start[0]-_target[0])**2.0 + (self._start[1]-_target[1])**2.0)**0.5 / 1500.0

        self._start_time = Clock.time

    def _make_attack(self):
        _direction = atan2(self._target[1]-PlayerData.raw_y, self._target[0]-PlayerData.raw_x)
        _hitbox = SpriteSolidColor(5, 15, (255, 255, 255))
        _hitbox.radians = _direction
        _attack = Attack(
            self.c_attack_data,
            self._target,
            degrees(_direction),
            _hitbox,
            Sprite(':assets:/textures/player/attack_placeholder.png', angle=degrees(_direction))
        )
        _attack.combat_manager.broadcast_player_attack(_attack)

    def animate(self) -> Tuple[float, float, float, Tuple[float, float]]:
        _t = Clock.length(self._start_time) / self._speed

        if _t >= 1.0:
            self._attack()
            self._coin.kill()
            PlayerData.invulnerable = False
            return 0.0, 0.0, 6.0, WindowData.mouse_pos
        PlayerData.invulnerable = True

        _x = lerp(self._start[0], self._target[0], ease_out(_t))
        _y = lerp(self._start[1], self._target[1], ease_out(_t))

        PlayerData.raw_position = _x, _y
        PlayerData.pos = int(_x), int(_y)

        _rotation = 0.0
        _theta = pi
        _radius = ((self._target[0]-PlayerData.raw_x)**2 + (self._target[1]-PlayerData.raw_y)**2)**0.5
        _target = self._target
        return _rotation, _theta, _radius, _target

    def complete(self) -> bool:
        return Clock.length(self._start_time) >= self._speed


from typing import Tuple
from math import atan2, cos, sin, pi, degrees

from arcade import Sprite, SpriteSolidColor, ease_in_out_sin, ease_out, lerp, load_textures

from src.animated_sprite import AnimatedSprite, AnimationData

from src.player.coin import Coin

from src.combat.weapon import Weapon
from src.combat.attack import AttackData, AttackFrame, AttackAnimation, Attack

from src.data import WindowData, PlayerData

from src.clock import Clock


class PlayerScythe(Weapon):

    def __init__(self, _parent_sprite_list):
        _scythe = Sprite(":assets:/textures/player/Scythe.png")
        super().__init__(_source=PlayerData, _weapon_sprite=_scythe, _parent_sprite_list=_parent_sprite_list)

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

    def farm(self):
        if self._current_attack:
            return

        _target_dx = WindowData.mouse_pos[0] - self._data.raw_x
        _target_dy = WindowData.mouse_pos[1] - self._data.raw_y
        _dist = (_target_dx ** 2 + _target_dy ** 2) ** 0.5

        for coin in PlayerData.coins:
            _dx = coin.position[0] - self._data.raw_x
            _dy = coin.position[1] - self._data.raw_y
            if _target_dx * _dx + _target_dy * _dx >= 0.98 and _dist >= self._data.attack_dist:
                coin.locked = True
                self._current_attack = CatchCoin(coin.position, coin)
                return

        self._current_attack = Farm()

    def swing(self):
        if self._current_attack:
            return

        _target_dx = WindowData.mouse_pos[0] - self._data.raw_x
        _target_dy = WindowData.mouse_pos[1] - self._data.raw_y
        _dist = (_target_dx ** 2 + _target_dy ** 2) ** 0.5

        for coin in PlayerData.coins:
            _dx = coin.position[0] - self._data.raw_x
            _dy = coin.position[1] - self._data.raw_y
            if _target_dx * _dx + _target_dy * _dx >= 0.98 and _dist >= self._data.attack_dist:
                coin.locked = True
                self._current_attack = CatchCoin(coin.position, coin)
                return

        _dist = self._data.attack_dist / _dist
        _target = self._data.raw_x + _target_dx * _dist, self._data.raw_y + _target_dy * _dist
        self._current_attack = Swipe(_target)

    def throw_coin(self):
        if self._current_attack:
            return

        _throw = PlayerData.throw_coin()
        if _throw:
            self._current_attack = ThrowCoin(WindowData.mouse_pos)


class PlayerTrowel(Weapon):

    def __init__(self, _parent_sprite_list):
        _scythe = Sprite(":assets:/textures/player/Trowel.png")
        super().__init__(_source=PlayerData, _weapon_sprite=_scythe, _parent_sprite_list=_parent_sprite_list)

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

    def swing(self):
        if self._current_attack:
            return

        _target_dx = WindowData.mouse_pos[0] - self._data.raw_x
        _target_dy = WindowData.mouse_pos[1] - self._data.raw_y
        _dist = (_target_dx ** 2 + _target_dy ** 2) ** 0.5

        for coin in PlayerData.coins:
            _dx = coin.position[0] - self._data.raw_x
            _dy = coin.position[1] - self._data.raw_y
            if _target_dx * _dx + _target_dy * _dx >= 0.98 and _dist <= 48:
                coin.locked = True
                self._current_attack = BounceCoin(coin.position, coin)
                return

        _dist = self._data.attack_dist / _dist
        _target = self._data.raw_x + _target_dx * _dist, self._data.raw_y + _target_dy * _dist
        self._current_attack = Swipe(_target)

    def throw_coin(self):
        if self._current_attack:
            return

        _throw = PlayerData.throw_coin()
        if _throw:
            self._current_attack = ThrowCoin(WindowData.mouse_pos)


class PlayerWateringCan(Weapon):

    def __init__(self, _parent_sprite_list):
        _watering_can: Sprite = Sprite(":assets:/textures/player/WateringCan.png")
        super().__init__(_source=PlayerData, _weapon_sprite=_watering_can, _parent_sprite_list=_parent_sprite_list)

    def update(self):
        if self._current_attack:
            self._rotation, self._theta, self._radius, _target = self._current_attack.animate()
            if self._current_attack.complete():
                self._current_attack = None
        else:
            self._rotation = 0
            self._theta = 0
            self._radius = 0.0

            _target = PlayerData.select_pos

        _dx, _dy = _target[0] - self._data.raw_x, _target[1] - self._data.raw_y
        _theta = atan2(_dy, _dx)

        _dist = (_dx**2+_dy**2)**0.5

        _x = self._data.raw_x + cos(_theta + self._theta) * (_dist + self._radius) - 8
        _y = self._data.raw_y + sin(_theta + self._theta) * (_dist + self._radius) + 8

        self._sprite.radians = self._rotation
        self._raw_position = _x, _y
        self._sprite.position = int(_x), int(_y)

    def water(self):
        if self._current_attack:
            return

        self._current_attack = Water()

    def throw_coin(self):
        if self._current_attack:
            return

        _throw = PlayerData.throw_coin()


class Swipe(AttackAnimation):
    c_swipe_frames: AnimationData = None

    c_positions: Tuple[AttackFrame, ...] = (  # Rotation, Theta, Radius, length
        AttackFrame(0.0, 0.0, 6.0, 0.05),
        AttackFrame(pi / 4, pi / 4, 12.0, 0.05),
        AttackFrame(pi * 0.8, 1.5 * pi, 14.0, 0.2),
        AttackFrame(pi * 0.75, 1.5 * pi, 14.0, 0.1),
        AttackFrame(pi * 0.1, pi / 6, 9.0, 0.1),
    )
    c_strike_frame: int = 4

    c_attack_data: AttackData = AttackData(
        1.0,
        0.0,
        0.4,
        0.0,
        wall_killed=False
    )

    def __init__(self, _target):
        if Swipe.c_swipe_frames is None:
            Swipe.c_swipe_frames = AnimationData(
                tuple(load_textures(":assets:/textures/player/ScytheSwipe.png", ((48*i, 0, 48, 64) for i in range(5)))),
                (0.05, 0.15, 0.1, 0.05, 0.05))

        super().__init__(_target)
        self._frame_start: float = 0.0
        self._current_frame: int = 0

        self._complete = False

    def _make_attack(self):
        _direction = atan2(self._target[1]-PlayerData.raw_y, self._target[0]-PlayerData.raw_x)
        _hitbox = SpriteSolidColor(48, 64, (255, 255, 255))
        _hitbox.radians = _direction
        _attack = Attack(
            self.c_attack_data,
            self._target,
            degrees(_direction),
            _hitbox,
            AnimatedSprite(Swipe.c_swipe_frames, self._target, degrees(_direction))
        )
        WindowData.game_view.combat_manager.broadcast_player_attack(_attack)

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

        _dx = WindowData.mouse_pos[0] - PlayerData.raw_x
        _dy = WindowData.mouse_pos[1] - PlayerData.raw_y
        _dist = PlayerData.attack_dist / (_dx ** 2 + _dy ** 2) ** 0.5
        _target = PlayerData.raw_x + _dx * _dist, PlayerData.raw_y + _dy * _dist

        self._target = _target

        return _rotation, _theta, _radius, _target

    def complete(self) -> bool:
        return self._complete


class Stab(AttackAnimation):
    c_stab_frames: AnimationData = None

    c_positions: Tuple[AttackFrame, ...] = (  # Rotation, Theta, Radius, length
        AttackFrame(0.0, 0.0, 6.0, 0.05),
        AttackFrame(pi / 4, pi / 4, 12.0, 0.05),
        AttackFrame(pi * 0.8, 1.5 * pi, 14.0, 0.2),
        AttackFrame(pi * 0.75, 1.5 * pi, 14.0, 0.1),
        AttackFrame(pi * 0.1, pi / 6, 9.0, 0.1),
    )
    c_strike_frame: int = 4

    c_attack_data: AttackData = AttackData(
        1.0,
        0.0,
        0.4,
        0.0,
        wall_killed=False
    )

    def __init__(self, _target):
        if Stab.c_stab_frames is None:
            Stab.c_stab_frames  = AnimationData(
                tuple(load_textures(":assets:/textures/player/TrowelStab.png",
                                    ((48 * i, 0, 48, 32) for i in range(5)))),
                (0.05, 0.15, 0.1, 0.05, 0.05))

        super().__init__(_target)
        self._frame_start: float = 0.0
        self._current_frame: int = 0

        self._complete = False

    def _make_attack(self):
        _direction = atan2(self._target[1] - PlayerData.raw_y, self._target[0] - PlayerData.raw_x)
        _hitbox = SpriteSolidColor(48, 64, (255, 255, 255))
        _hitbox.radians = _direction
        _attack = Attack(
            self.c_attack_data,
            self._target,
            degrees(_direction),
            _hitbox,
            AnimatedSprite(Stab.c_stab_frames , self._target, degrees(_direction))
        )
        WindowData.game_view.combat_manager.broadcast_player_attack(_attack)

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

        _dx = WindowData.mouse_pos[0] - PlayerData.raw_x
        _dy = WindowData.mouse_pos[1] - PlayerData.raw_y
        _dist = PlayerData.attack_dist / (_dx ** 2 + _dy ** 2) ** 0.5
        _target = PlayerData.raw_x + _dx * _dist, PlayerData.raw_y + _dy * _dist

        self._target = _target

        return _rotation, _theta, _radius, _target

    def complete(self) -> bool:
        return self._complete


class Farm(AttackAnimation):
    c_positions: Tuple[AttackFrame, ...] = (  # Rotation, Theta, Radius, length
        AttackFrame(0.0, 0.0, 6.0, 0.05),
        AttackFrame(pi / 4, pi / 4, 12.0, 0.05),
        AttackFrame(pi * 0.8, 1.5 * pi, 14.0, 0.2),
        AttackFrame(pi * 0.75, 1.5 * pi, 14.0, 0.1),
        AttackFrame(pi * 0.1, pi / 6, 9.0, 0.1),
    )

    c_dig_frame: int = 2

    def __init__(self):
        super().__init__(PlayerData.select_pos)
        self._hitbox = SpriteSolidColor(1, 1, (255, 255, 255))
        self._hitbox.position = self._target

        self._frame_start: float = 0.0
        self._current_frame: int = 0

        self._complete = False

    def _make_attack(self):
        WindowData.game_view.try_dig(self._hitbox)
        WindowData.game_view.try_harvest(self._hitbox)

    def animate(self) -> Tuple[float, float, float, Tuple[float, float]]:
        _frame_values: AttackFrame = self.c_positions[self._current_frame]

        _next_frame = (self._current_frame + 1) % len(self.c_positions)
        _target_values: AttackFrame = self.c_positions[_next_frame]

        _t = Clock.length(self._frame_start) / _frame_values.length

        if _t >= 1.0:
            self._frame_start = Clock.time
            self._current_frame = _next_frame

            if _next_frame == self.c_dig_frame:
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


class Water(AttackAnimation):
    c_positions: Tuple[AttackFrame, ...] = (  # Rotation, Theta, Radius, length
        AttackFrame(0.0, 0.0, 0.0, 0.3),
        AttackFrame(-pi/6, 0.0, 0.0, 0.5),
        AttackFrame(-pi/8, 0.0, 0.0, 0.2),
    )

    c_dig_frame: int = 1

    def __init__(self):
        super().__init__(PlayerData.select_pos)
        self._hitbox = SpriteSolidColor(1, 1, (255, 255, 255))
        self._hitbox.position = self._target

        self._frame_start: float = 0.0
        self._current_frame: int = 0

        self._complete = False

    def _make_attack(self):
        WindowData.game_view.try_water(self._hitbox)

    def animate(self) -> Tuple[float, float, float, Tuple[float, float]]:
        _frame_values: AttackFrame = self.c_positions[self._current_frame]

        _next_frame = (self._current_frame + 1) % len(self.c_positions)
        _target_values: AttackFrame = self.c_positions[_next_frame]

        _t = Clock.length(self._frame_start) / _frame_values.length

        if _t >= 1.0:
            self._frame_start = Clock.time
            self._current_frame = _next_frame

            if _next_frame == self.c_dig_frame:
                self._attack()

            if _next_frame == 0:
                self._complete = True

        _rotation = lerp(_frame_values.rotation, _target_values.rotation, _t)
        _theta = lerp(_frame_values.theta, _target_values.theta, _t)
        _radius = lerp(_frame_values.radius, _target_values.radius, _t)

        _target = self._target

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


class BounceCoin(AttackAnimation):
    c_attack_data: AttackData = AttackData(
        3.0,
        0.0,
        2.0,
        240.0,
        0.0,
        120.0
    )

    def __init__(self, _target, _coin: Coin):
        if Stab.c_stab_frames is None:
            Stab.c_stab_frames = AnimationData(
                tuple(load_textures(":assets:/textures/player/TrowelStab.png",
                                    ((48 * i, 0, 48, 32) for i in range(5)))),
                (0.05, 0.15, 0.1, 0.05, 0.05))
        super().__init__(_target)
        self._coin = _coin

        self._start_time = Clock.time

    def _make_attack(self):
        _source = WindowData.game_view.boss_manager.boss.raw_pos
        _direction = atan2(_source[1] - self._target[1], _source[0] - self._target[0])
        _hitbox = SpriteSolidColor(5, 5, (255, 255, 255))
        _hitbox.radians = _direction
        _attack = Attack(
            self.c_attack_data,
            self._target,
            degrees(_direction),
            _hitbox,
            AnimatedSprite(Stab.c_stab_frames , self._target, degrees(_direction))
        )
        WindowData.game_view.combat_manager.broadcast_player_attack(_attack)

    def animate(self) -> Tuple[float, float, float, Tuple[float, float]]:
        self._attack()
        self._coin.kill()
        return 0.0, 0.0, 6.0, WindowData.mouse_pos

    def complete(self) -> bool:
        return True


class CatchCoin(AttackAnimation):
    c_coin_dash: AnimationData = None

    c_attack_data: AttackData = AttackData(
        1.5,
        0.0,
        2.0,
        160.0,
        0.0,
        80.0
    )

    def __init__(self, _target, _coin: Coin):
        if CatchCoin.c_coin_dash is None:
            CatchCoin.c_coin_dash = AnimationData(
                tuple(load_textures(":assets:/textures/player/TrowelStab.png", ((48*i, 0, 48, 32) for i in range(5)))),
                (0.1, 0.1, 0.1, 0.1, 0.1),
                loop=True
            )
        super().__init__(_target)
        self.do_attacks = not PlayerData.passive
        self._coin = _coin
        self._start = PlayerData.raw_position

        self._speed = ((self._start[0]-_target[0])**2.0 + (self._start[1]-_target[1])**2.0)**0.5 / 1500.0

        self._start_time = Clock.time

    def _make_attack(self):
        _direction = atan2(self._target[1]-self._start[1], self._target[0]-self._start[0])
        _hitbox = SpriteSolidColor(5, 15, (255, 255, 255))
        _hitbox.radians = _direction
        _attack = Attack(
            self.c_attack_data,
            self._target,
            degrees(_direction),
            _hitbox,
            AnimatedSprite(CatchCoin.c_coin_dash, self._target, degrees(_direction))
        )
        WindowData.game_view.combat_manager.broadcast_player_attack(_attack)

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

        PlayerData.raw_pos = _x, _y

        _rotation = 0.0
        _theta = pi
        _radius = ((self._target[0]-PlayerData.raw_x)**2 + (self._target[1]-PlayerData.raw_y)**2)**0.5
        _target = self._target
        return _rotation, _theta, _radius, _target

    def complete(self) -> bool:
        return Clock.length(self._start_time) >= self._speed


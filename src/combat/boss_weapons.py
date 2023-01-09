from typing import Tuple
from math import atan2, cos, sin, pi, degrees

from arcade import Sprite, SpriteSolidColor, ease_in_out_sin, ease_out, lerp, load_texture

from src.animated_sprite import AnimatedSprite, AnimationData

from src.combat.weapon import Weapon
from src.combat.attack import AttackData, AttackFrame, AttackAnimation, Attack

from src.data import WindowData

from src.clock import Clock


class Sweep(AttackAnimation):
    c_blade: AnimationData = None

    c_data: AttackData = AttackData(
        2.0,
        350.0,
        1/60,
        0.0,
        0.0,
        wall_killed=False
    )

    c_start_frame = AttackFrame(0.0, pi/2, 25.0, 1.0)

    def __init__(self, _target):
        if Sweep.c_blade is None:
            Sweep.c_blade = AnimationData((load_texture(":assets:/textures/enemies/FlameRing.png"),), (1.0,), True)
        super().__init__(_target)
        self._start_time = Clock.time
        self._theta = 0.0

    def _make_attack(self):

        _direction = self._theta
        _hitbox = SpriteSolidColor(38, 48, (255, 255, 255, 255))
        _hitbox.radians = _direction
        _x, _y = self._target[0]+cos(_direction)*45.0, self._target[1]+sin(_direction)*45.0
        _attack = Attack(
            self.c_data,
            (_x, _y),
            degrees(_direction),
            _hitbox,
            AnimatedSprite(Pulse.c_blade, (_x, _y), angle=degrees(_direction))
        )
        WindowData.game_view.combat_manager.broadcast_enemy_attack(_attack)

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
        return Clock.length(self._start_time) >= 18.0


class Pulse(AttackAnimation):
    c_blade: AnimationData = None
    c_data: AttackData = AttackData(
        1.0,
        0.0,

        12.0,

        160.0,
        60.0,
        80.0,
        scale_velocity=-0.2
    )

    c_start_frame = AttackFrame(0.0, pi/2, 25.0, 1.0)

    def __init__(self, _target):
        if Pulse.c_blade is None:
            Pulse.c_blade = AnimationData((load_texture(":assets:/textures/enemies/FlameSmall.png"),), (1.0,), True)
        super().__init__(_target)
        self._start_time = Clock.time
        self._theta = 0.0

        self._last_shot: float = 0.0

    def _make_attack(self):
        _direction = self._theta
        _hitbox = SpriteSolidColor(48, 48, (255, 255, 255, 255))
        _hitbox.radians = _direction
        _x, _y = self._target[0]+cos(_direction)*45.0, self._target[1]+sin(_direction)*45.0
        _attack = Attack(
            self.c_data,
            (_x, _y),
            degrees(_direction),
            _hitbox,
            AnimatedSprite(Pulse.c_blade, (_x, _y), angle=degrees(_direction))
        )
        WindowData.game_view.combat_manager.broadcast_enemy_attack(_attack)

        _direction = -self._theta
        _hitbox = SpriteSolidColor(48, 48, (255, 255, 255, 255))
        _hitbox.radians = _direction
        _x, _y = self._target[0] + cos(_direction) * 45.0, self._target[1] + sin(_direction) * 45.0
        _attack = Attack(
            self.c_data,
            (_x, _y),
            degrees(_direction),
            _hitbox,
            AnimatedSprite(Pulse.c_blade, (_x, _y), angle=degrees(_direction))
        )
        WindowData.game_view.combat_manager.broadcast_enemy_attack(_attack)

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

            if Clock.length(self._last_shot) > 0.15:
                self._attack()
                self._last_shot = Clock.time

        self._theta = _theta

        return _rotation, _theta, _radius, _target

    def complete(self) -> bool:
        return Clock.length(self._start_time) >= 6.0


class Slam(AttackAnimation):
    c_slam_animation: AnimationData = None

    c_frames: Tuple[AttackFrame, ...] = (
        AttackFrame(0.0, pi / 2, 25.0, 1.0),
        AttackFrame(0.0, pi / 2, 50.0, 0.3),
        AttackFrame(pi/6, pi / 2, 50.0, 0.3),
        AttackFrame(-pi/6, pi / 2, 50.0, 0.3),
        AttackFrame(pi/6, pi / 2, 50.0, 0.3),
        AttackFrame(-pi/6, pi / 2, 50.0, 0.1),
        AttackFrame(0.0, pi / 2, -40.0, 0.1),
        AttackFrame(0.0, pi / 2, -30.0, 1.0)
    )

    c_attack_frame: int = 7

    c_attack_data: AttackData = AttackData(
        1.0,
        600.0,

        1.0,

        0.0,
        0.0,
        0.0,
        0.0,
        2.5
    )

    def __init__(self, _target):
        if Slam.c_slam_animation is None:
            Slam.c_slam_animation = AnimationData((load_texture(":assets:/textures/enemies/Pulse.png"),), (1.0,), True)

        super().__init__(_target)
        self._start_time: float = Clock.time
        self._current_frame: int = 0

        self._complete = False

    def _make_attack(self):
        _attack = Attack(
            self.c_attack_data,
            self._target,
            0.0,
            SpriteSolidColor(96, 64, (255, 255, 255)),
            AnimatedSprite(Slam.c_slam_animation, self._target)
        )
        WindowData.game_view.combat_manager.broadcast_enemy_attack(_attack)

    def animate(self) -> Tuple[float, float, float, Tuple[float, float]]:
        _frame_values: AttackFrame = self.c_frames[self._current_frame]

        _next_frame = (self._current_frame + 1) % len(self.c_frames)
        _target_values: AttackFrame = self.c_frames[_next_frame]

        _t = Clock.length(self._start_time) / _frame_values.length

        if _t >= 1.0:
            self._start_time = Clock.time
            self._current_frame = _next_frame

            if _next_frame == self.c_attack_frame:
                self._attack()

            if _next_frame == 0:
                self._complete = True

        _rotation = lerp(_frame_values.rotation, _target_values.rotation, _t)
        _theta = lerp(_frame_values.theta, _target_values.theta, _t)
        _radius = lerp(_frame_values.radius, _target_values.radius, _t)
        _target = self._target

        return _rotation, _theta, _radius, _target


class GeorgieHead(Weapon):

    def __init__(self, _source, _parent_sprite_list, _weakspot):
        _head = Sprite(":assets:/textures/enemies/GeorgieHead.png")
        super().__init__(_source, _head, _parent_sprite_list)

        self._weakspot = _weakspot

        self.show_weapon()

    @property
    def attacking(self):
        return self._current_attack is not None

    def show_weapon(self):
        super().show_weapon()

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
                self.stop_attack()
        else:
            _rot, _theta, _radius = 0.0, pi/2, 25.0
            self._rotation, self._theta, self._radius = _rot, _theta, _radius
            _target = WindowData.mouse_pos

        _x, _y = self._data.raw_x + cos(_theta) * _radius, self._data.raw_y + sin(_theta) * _radius
        n_x, n_y = self._data.raw_x - cos(_theta) * _radius, self._data.raw_y - sin(_theta) * _radius

        self._sprite.radians = _rot
        self._weakspot.radians = -_rot
        self._raw_position = _x, _y
        self._sprite.position = int(_x), int(_y)
        self._weakspot.position = int(n_x), int(n_y)

    def slam(self):
        if self._current_attack:
            return

        self._current_attack = Slam(self._data.raw_pos)

    def sweep(self):
        if self._current_attack:
            return

        self._current_attack = Sweep(self._data.raw_pos)

    def pulse(self):
        if self._current_attack:
            return

        self._current_attack = Pulse(self._data.raw_pos)



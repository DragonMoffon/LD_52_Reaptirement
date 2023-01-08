from typing import Tuple, NamedTuple
from math import radians, cos, sin

from arcade import Sprite

if False:
    from src.combat.combat import CombatManager

from src.clock import Clock


class AttackData(NamedTuple):
    damage: float
    knockback: float

    duration: float

    start_velocity: float
    angle_velocity: float = 0.0
    acceleration: float = 0.0

    wall_killed: bool = True


class AttackFrame(NamedTuple):
    rotation: float
    theta: float
    radius: float
    length: float


class AttackAnimation:

    def __init__(self, _target: Tuple[float, float]):
        self._target: Tuple[float, float] = _target
        self.do_attacks: bool = True

    def _make_attack(self):
        pass

    def _attack(self):
        if self.do_attacks:
            self._make_attack()

    def animate(self) -> Tuple[float, float, float, Tuple[float, float]]:
        pass

    def complete(self) -> bool:
        pass


class Attack:
    combat_manager: "CombatManager" = None

    @staticmethod
    def set_manager(_manager: "CombatManager"):
        Attack.combat_manager = _manager

    def __init__(self, data: AttackData, start_pos: Tuple[float, float], start_direction: float,
                 hitbox: Sprite, attack_sprite: Sprite):
        self._damage: float = data.damage
        self._knockback: float = data.knockback

        self._hitbox: Sprite = hitbox
        self._attack_sprite: Sprite = attack_sprite

        self._hitbox.position = start_pos
        self._attack_sprite.position = int(start_pos[0]), int(start_pos[1])

        self._position: start_pos

        self._direction: float = start_direction
        self._velocity: float = data.start_velocity
        self._angle_velocity: float = data.angle_velocity
        self._acceleration: float = data.acceleration

        self._wall_killed: bool = data.wall_killed

        self._spawn_time: float = Clock.time
        self._duration: float = data.duration

        self.struck: bool = False

    def update(self):
        self._direction += self._angle_velocity * Clock.delta_time
        self._velocity += self._acceleration * Clock.delta_time

        _r = radians(self._direction)
        _dx, _dy = cos(_r) * self._velocity, sin(_r) * self._velocity

        _x = self._hitbox.center_x + _dx * Clock.delta_time
        _y = self._hitbox.center_y + _dy * Clock.delta_time

        self._hitbox.position = _x, _y
        self._attack_sprite.position = int(_x), int(_y)
        self._attack_sprite.angle = self._direction

    def age(self):
        return Clock.length(self._spawn_time) / self._duration

    def kill(self):
        self._attack_sprite.remove_from_sprite_lists()

    def hit(self):
        self.struck = True

    @property
    def sprite(self):
        return self._attack_sprite

    @property
    def hitbox(self):
        return self._hitbox

    @property
    def damage(self):
        return self._damage

    @property
    def knockback(self):
        return self._knockback

    @property
    def velocity(self):
        return self._velocity

    @property
    def direction(self):
        return self._direction

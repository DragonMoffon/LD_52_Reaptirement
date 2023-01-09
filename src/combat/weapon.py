from typing import Tuple

from arcade import Sprite, SpriteList

from src.combat.attack import AttackAnimation

from src.clock import Clock


class Weapon:

    def __init__(self, _source: any, _weapon_sprite: Sprite, _parent_sprite_list: SpriteList):
        self._rotation: float = 0.0
        self._theta: float = 0.0
        self._radius: float = 0.0

        self._target: Tuple[float, float] = (0.0, 0.0)

        self._data: any = _source

        self._raw_position: Tuple[float, float] = (0.0, 0.0)
        self._sprite: Sprite = _weapon_sprite
        self._parent_sprite_list: SpriteList = _parent_sprite_list

        self._current_attack: AttackAnimation | None = None
        self._stopping_attack: float = 0.0

    @property
    def sprite(self):
        return self._sprite

    @property
    def raw_x(self):
        return self._raw_position[0]

    @property
    def raw_y(self):
        return self._raw_position[1]

    @property
    def can_attack(self):
        return self._current_attack is not None

    def stop_attack(self):
        self._stopping_attack = Clock.time

    def hide_weapon(self):
        self._sprite.remove_from_sprite_lists()

    def show_weapon(self):
        if self._sprite in self._parent_sprite_list:
            return
        self._parent_sprite_list.append(self._sprite)

    def update(self):
        pass



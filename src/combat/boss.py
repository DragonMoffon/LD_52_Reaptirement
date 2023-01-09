from typing import Tuple, List
from random import random, randint

from arcade import Sprite, SpriteSolidColor, SpriteList, load_textures, lerp

from src.animated_sprite import AnimatedSprite, AnimationData

from src.combat.weapon import Weapon
from src.combat.boss_weapons import GeorgieHead

from src.data import PlayerData, WindowData, SaveData


class Boss:

    def __init__(self, position: Tuple[float, float], health):
        self._health = health
        self._max_health = health

        self._sprite_renderer: SpriteList = SpriteList()

        self._sprite: AnimatedSprite = None
        self._weak_spot: Sprite = None
        self._hitbox: Sprite = None

        self._weapon: Weapon = None

        self._raw_position: Tuple[float, float] = position

        self._current_task: str = None

        self.prepare_sprites()

    def prepare_sprites(self):
        raise NotImplementedError()

    @property
    def weapon(self):
        return self._weapon

    @property
    def raw_x(self):
        return self._raw_position[0]

    @property
    def raw_y(self):
        return self._raw_position[1]

    @property
    def raw_pos(self):
        return self._raw_position

    @raw_pos.setter
    def raw_pos(self, value: Tuple[float, float]):
        self._raw_position = value

        self._sprite.position = int(value[0]), int(value[1])
        self._hitbox.position = value

    @property
    def sprite(self):
        return self._sprite

    @property
    def hitbox(self):
        return self._hitbox

    @property
    def weakspot(self):
        return self._weak_spot

    @property
    def health(self):
        return self._health

    @property
    def max_health(self):
        return self._max_health

    def draw(self):
        self._sprite_renderer.draw(pixelated=True)

    def update(self):
        pass

    def take_damage(self, damage: float):
        damage = min(damage, self._health)
        SaveData.damage_done += damage

        self._health -= damage

        if self._health <= 0.0:
            SaveData.number_of_kills += 1
            WindowData.game_view.show_victory()


class GeorgieBoss(Boss):
    c_body_animation: AnimationData = None
    c_action_map: Tuple[str, str, str, str] = ("Move", "Sweep", "Pulse", "Slam")

    def __init__(self, position: Tuple[float, float]):
        _health = 48 + int(24 * SaveData.number_of_kills / 16) * 16
        super().__init__(position, _health)

        self._target_location: Tuple[int, int] = None
        self._move_speed: float = 0.01

        self._weapon.show_weapon()

        self._last_action: str = ""
        self._jitter_chance: float = 0.0
        self._move_chance: float = 0.0

    def prepare_sprites(self):
        if GeorgieBoss.c_body_animation is None:
            GeorgieBoss.c_body_animation = AnimationData(
                tuple(load_textures(":assets:/textures/enemies/Georgie.png", ((96*i, 0, 96, 64) for i in range(4)))),
                (1.0, 1.0, 1.0, 1.0),
                loop=True
            )

        self._sprite = AnimatedSprite(GeorgieBoss.c_body_animation, self.raw_pos)
        self._sprite_renderer.append(self._sprite)
        self._weak_spot = Sprite(":assets:/textures/enemies/GeorgieCrown.png")
        self._sprite_renderer.append(self._weak_spot)
        self._hitbox = SpriteSolidColor(int(self._sprite.width), int(self._sprite.height), (255, 255, 255))

        self._weapon = GeorgieHead(self, self._sprite_renderer, self.weakspot)

    def update(self):
        self._sprite.update_texture()

        if self._current_task is None:
            self._target_location = None
            _dx, _dy = PlayerData.raw_x - self.raw_x, PlayerData.raw_y - self.raw_y
            _dist = (_dx**2+_dy**2)**0.5

            _ideal = 0 if random() < self._move_chance else 1

            if _ideal != 0:
                self._move_chance += 0.05
            else:
                self._move_chance = 0.0

            if _dist <= 112:
                _ideal = 3
            elif _dist >= 240:
                _ideal = 2

            if random() < self._jitter_chance:
                _ideal = (_ideal + randint(-2, 2)) % 4
            else:
                self._jitter_chance += 0.25

            _next_task = GeorgieBoss.c_action_map[_ideal]
            if _next_task == self._last_action and random() > 0.25:
                _ideal = (_ideal + (1 - 2 * randint(0, 1))) % 4
                _next_task = GeorgieBoss.c_action_map[_ideal]

            self._current_task = _next_task
        elif self._current_task == "Move":
            if self._target_location is None:
                _bounds = WindowData.game_view.current_map.bounds
                _x = int(randint(_bounds[0]+192, _bounds[2]-192) / 16) * 16
                _y = int(randint(_bounds[1]+160, _bounds[3]-160) / 16) * 16
                self._target_location = (_x, _y)

            _dx, _dy = self._target_location[0] - self.raw_x, self._target_location[1] - self.raw_y
            _dist = (_dx**2+_dy**2)
            if _dist > 64**2:
                _x = lerp(self.raw_x, self._target_location[0], self._move_speed)
                _y = lerp(self.raw_y, self._target_location[1], self._move_speed)

                self.raw_pos = _x, _y
            else:
                self._target_location = None
                self._current_task = None

        elif self._current_task == "Sweep":
            if self._target_location is None:
                self._target_location = self.raw_pos
                self._weapon.sweep()
            elif not self._weapon.attacking:
                self._last_action = self._current_task
                self._current_task = None
        elif self._current_task == "Pulse":
            if self._target_location is None:
                self._target_location = self.raw_pos
                self._weapon.pulse()
            elif not self._weapon.attacking:
                self._last_action = self._current_task
                self._current_task = None
        elif self._current_task == "Slam":
            if self._target_location is None:
                self._target_location = self.raw_pos
                self._weapon.slam()
            elif not self._weapon.attacking:
                self._last_action = self._current_task
                self._current_task = None

        self._weapon.update()


class BossManager:

    def __init__(self):
        self._current_boss: Boss = None

    @property
    def boss(self):
        return self._current_boss

    def reset(self):
        self._current_boss = None

    def generate_georgie(self, position: Tuple[float, float]):
        self._current_boss = GeorgieBoss(position)

        return self._current_boss.hitbox, self._current_boss.weakspot

    def damage_boss(self, damage: int):
        self._current_boss.take_damage(damage)

    def update(self):
        if self._current_boss is not None:
            self._current_boss.update()

    def draw(self):
        if self._current_boss is not None:
            self._current_boss.draw()

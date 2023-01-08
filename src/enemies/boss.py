from typing import Tuple, List

from arcade import Sprite, SpriteSolidColor, SpriteList

from src.data import WindowData

from src.combat.attack import AttackData
from src.combat.weapon import Weapon
from src.combat.boss_weapons import GeorgieHead
from src.enemies.event_manager import EnemyEventManager


class Boss:

    def __init__(self):
        self._health = 1.0

        self._sprite_renderer: SpriteList = SpriteList()
        self._attacks: List[AttackData] = []

        self._sprite: Sprite = Sprite(":assets:/textures/enemies/georgie_placeholder.png")
        self._sprite.position = WindowData.down_scale_resolution[0]//2, WindowData.down_scale_resolution[1]//2

        self._hitbox: Sprite = SpriteSolidColor(int(self._sprite.width), int(self._sprite.height), (255, 255, 255, 255))

        self._weak_spots: SpriteList = SpriteList()

        self._sprite_renderer.append(self._sprite)

        self._event_manager = EnemyEventManager(self)

        self._raw_position: Tuple[float, float] = self._sprite.position
        self._hitbox.position = self._raw_position

        self._current_task: str = None

        self._weapon: Weapon = None

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

    @property
    def sprite(self):
        return self._sprite

    @property
    def hitbox(self):
        return self._hitbox

    @property
    def weakspots(self):
        return self._weak_spots

    @property
    def event_manager(self):
        return self._event_manager

    def draw(self):
        self._sprite_renderer.draw(pixelated=True)

    def update(self):
        pass

    def take_damage(self, damage: float):
        self._health -= damage

        if self._health <= 0.0:
            print("I'm dead")


class GeorgieBoss(Boss):

    def __init__(self):
        super().__init__()

        self._target_location: Tuple[int, int] = (0, 0)
        self._move_speed: float = 45.0

        self._weapon = GeorgieHead(self, self._sprite_renderer)
        self._weapon.show_weapon()

    def update(self):
        if self._current_task is None:
            self._current_task = "Sweep"
        elif self._current_task == "Move":
            pass
        elif self._current_task == "Sweep":
            self._weapon.sweep()
        elif self._current_task == "Pulse":
            pass
        elif self._current_task == "Slam":
            pass

        self._weapon.update()


class BossManager:

    def __init__(self):
        self._current_boss: Boss = None
        self._boss_arena = None

        self.rewards = None

    def generate_georgie(self):
        self._current_boss = GeorgieBoss()

        return self._current_boss.hitbox, self._current_boss.weakspots, self._current_boss.event_manager

    def update(self):
        if self._current_boss is not None:
            self._current_boss.update()

    def draw(self):
        if self._current_boss is not None:
            self._current_boss.draw()

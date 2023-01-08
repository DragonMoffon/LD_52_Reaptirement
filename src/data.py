from arcade import Camera, Sprite

from typing import Tuple

from src.clock import Clock

if False:
    from src.vignette import Vignette
    from src.player.event_manager import PlayerEventManager


class _WindowData:

    def __init__(self):
        self.update_rate: float = 0.0

        self.full_screen: bool = False

        self._screen_resolution: Tuple[int, int] = (480, 270)
        self._down_scale_resolution: Tuple[int, int] = (480, 270)
        self._up_scale_multiplier: float = 1.0
        self._border_gap: Tuple[float, float] = (0.0, 0.0)

        self._scaled_viewport: Tuple[int, int, int, int] = (0, 0, 0, 0)
        self._scaled_projection: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)

        self._mouse_position: Tuple[int, int] = (0, 0)
        self._true_mouse_position: Tuple[int, int] = (0, 0)

        self.vignette: "Vignette" = None
        self.camera: Camera = None

    def set_vignette(self, vignette: "Vignette"):
        self.vignette = vignette

    def create_camera(self):
        self.camera = Camera(projection=self._scaled_projection, viewport=self._scaled_viewport)

    @property
    def mouse_pos(self):
        return self._mouse_position

    @property
    def true_mouse_position(self):
        return self._true_mouse_position

    @true_mouse_position.setter
    def true_mouse_position(self, value: Tuple[int, int]):
        self._true_mouse_position = value

        _x = (value[0] - self._border_gap[0] / 2) // self._up_scale_multiplier
        _y = (value[1] - self._border_gap[1] / 2) // self._up_scale_multiplier
        self._mouse_position = (_x, _y)

    def set_resolution_data(self, screen: Tuple[int, int], down_scale: Tuple[int, int], multiplier: float):
        self._screen_resolution = screen
        self._down_scale_resolution = down_scale

        self._up_scale_multiplier = multiplier

        self._border_gap = screen[0] - down_scale[0] * multiplier, screen[1] - down_scale[1] * multiplier
        self._scaled_viewport = (0, 0, down_scale[0], down_scale[1])
        self._scaled_projection = (0.0, down_scale[0], 0.0, down_scale[1])

        self.create_camera()

    @property
    def screen_resolution(self):
        return self._screen_resolution

    @screen_resolution.setter
    def screen_resolution(self, value: Tuple[int, int]):
        self._screen_resolution = value
        self._border_gap = value[0] - self._down_scale_resolution[0], value[1] - self.down_scale_resolution[1]

    @property
    def down_scale_resolution(self):
        return self._down_scale_resolution

    @down_scale_resolution.setter
    def down_scale_resolution(self, value: Tuple[int, int]):
        self._down_scale_resolution = value
        self._border_gap = (self._screen_resolution[0] - value[0] * self._up_scale_multiplier,
                            self._screen_resolution[1] - value[1] * self._up_scale_multiplier)

        self._scaled_viewport = (0, 0, value[0], value[1])
        self._scaled_projection = (0.0, value[0], 0.0, value[1])

    @property
    def up_scale_multiplier(self):
        return self._up_scale_multiplier

    @up_scale_multiplier.setter
    def up_scale_multiplier(self, value: float):
        self._up_scale_multiplier = float
        self._border_gap = (self._screen_resolution[0] - self._down_scale_resolution[0] * value,
                            self._screen_resolution[1] - self._down_scale_resolution[1] * value)

    @property
    def scaled_viewport(self):
        return self._scaled_viewport

    @property
    def scaled_projection(self):
        return self._scaled_projection


WindowData = _WindowData()


class _PlayerUniversalData:

    def __init__(self):
        self.max_health: float = 48.0
        self.current_health: float = self.max_health

        self.max_speed: float = 60.0

        self.stamina: float = 1.0

        self.raw_position: Tuple[float, float] = (0.0, 0.0)
        self.velocity: Tuple[float, float] = (0.0, 0.0)

        self.primary_sprite: Sprite = None

        self.hitbox: Sprite = None

        self.event_manager: PlayerEventManager = None

        self.invulnerable: bool = False

        self.max_coins: int = 1
        self.attack_dist: float = 15.0

    def set_primary_sprite(self, sprite: Sprite):
        self.primary_sprite = sprite

    def set_hitbox(self, sprite: Sprite):
        self.hitbox = sprite

    def set_event_manager(self, manager: "PlayerEventManager"):
        self.event_manager = manager

    def take_damage(self, damage: float):
        self.current_health -= damage

        if self.current_health <= 0.0:
            print("your dead mo fo!")
            Clock.tick_speed = 0.0

    @property
    def raw_x(self):
        return self.raw_position[0]

    @property
    def raw_y(self):
        return self.raw_position[1]

    @property
    def pos(self):
        return self.primary_sprite.position

    @pos.setter
    def pos(self, value: Tuple[float, float]):
        self.primary_sprite.position = value

    @property
    def x(self):
        return self.primary_sprite.center_x

    @x.setter
    def x(self, value: float):
        self.primary_sprite.center_x = value

    @property
    def y(self):
        return self.primary_sprite.center_y

    @y.setter
    def y(self, value: float):
        self.primary_sprite.center_y = value


PlayerData = _PlayerUniversalData()

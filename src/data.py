from typing import Tuple, NamedTuple, List, Dict
from json import dump, load
from random import randint
from math import ceil


from arcade import Camera, Sprite, get_window, SpriteList
from arcade.resources import resolve_resource_path

from src.clock import Clock

from src.player.coin import Coin

if False:
    from src.vignette import Vignette
    from src.views.game import GameView
    from src.window import AppWindow
    from src.farm.tools import ToolBelt
    from src.player.consumables import Consumable
    from src.combat.attack import Attack


class _SaveData:

    def __init__(self):
        self.products_brought: int = 0
        self.currency_gained: int = 0
        self.crops_harvested: int = 0
        self.crops_consumed: int = 0
        self.current_currency: int = 100

        self.number_of_kills: int = 1
        self.damage_done: int = 0
        self.damage_taken: int = 0

        self.trowel_collected: bool = False
        self.potency_level: int = 0
        self.coin_level: int = 0
        self.capacity_level: int = 0

        self.last_victory: float = 0.0

    def reset(self):
        self.products_brought: int = 0
        self.currency_gained: int = 0
        self.crops_harvested: int = 0
        self.crops_consumed: int = 0
        self.current_currency: int = 100

        self.number_of_kills: int = 0
        self.damage_done: int = 0
        self.damage_taken: int = 0

        self.trowel_collected: bool = False
        self.potency_level: int = 0
        self.coin_level: int = 0
        self.capacity_level: int = 0

        self.last_victory: float = 0.0

    @property
    def toll_cost(self):
        return 150 + self.number_of_kills*50

    def to_dict(self):
        return {
            'p_b': self.products_brought,
            'c_g': self.currency_gained,
            'u_u': self.current_currency,
            'c_h': self.crops_harvested,
            'c_c': self.crops_consumed,
            'n_k': self.number_of_kills,
            'd_d': self.damage_done,
            'd_t': self.damage_taken,
            't_c': self.trowel_collected,
            'p_l': self.potency_level,
            'c_l': self.coin_level,
            'a_l': self.capacity_level
        }

    def from_dict(self, _dict):
        self.products_brought = _dict['p_b']
        self.currency_gained = _dict['c_g']
        self.current_currency = _dict['u_u']
        self.crops_harvested = _dict['c_h']
        self.crops_consumed = _dict['c_c']
        self.number_of_kills = _dict['n_k']
        self.damage_done = _dict['d_d']
        self.damage_taken = _dict['d_t']
        self.trowel_collected = _dict['t_c']
        self.potency_level = _dict['p_l']
        self.coin_level = _dict['c_l']
        self.capacity_level = _dict['a_l']

    def load_from_file(self):
        _src = resolve_resource_path(":assets:/save.json")
        with open(_src) as _file:
            self.from_dict(load(_file))

    def save_to_file(self):
        _data = self.to_dict()
        _src = resolve_resource_path(":assets:/save.json")
        with open(_src, "w+") as _file:
            dump(_data, _file)

    def reset_save(self):
        self.reset()
        self.save_to_file()


SaveData = _SaveData()


class _WindowData:

    def __init__(self):
        self.update_rate: float = 0.0
        self.window: "AppWindow" = None
        self.game_view: "GameView" = None

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
        self.locked_camera: Camera = None
        self.tracked_camera: Camera = None
        self.full_screen_camera: Camera = None

    def reset(self):
        self._mouse_position: Tuple[int, int] = (0, 0)
        self._true_mouse_position: Tuple[int, int] = (0, 0)

    def set_vignette(self, vignette: "Vignette"):
        self.vignette = vignette

    def set_window(self):
        self.window = get_window()

    def set_game_view(self, game_view):
        self.game_view = game_view

    def create_cameras(self):
        self.locked_camera = Camera(projection=self._scaled_projection, viewport=self._scaled_viewport)
        self.tracked_camera = Camera(projection=self._scaled_projection, viewport=self._scaled_viewport)

    @property
    def mouse_pos(self):
        return (self.tracked_camera.position[0] + self._mouse_position[0],
                self.tracked_camera.position[1] + self._mouse_position[1])

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

        self.create_cameras()

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
        self.max_health: int = 6
        self.current_health: int = self.max_health

        self.max_speed: float = 75.0

        self.raw_position: Tuple[float, float] = (0.0, 0.0)
        self.velocity: Tuple[float, float] = (0.0, 0.0)
        self.knockback: Tuple[float, float] = (0.0, 0.0)

        self.primary_sprite: Sprite = None

        self.hitbox: Sprite = None

        self._invulnerable: bool = False
        self.passive: bool = False
        self.control: bool = True

        self.payed_toll: bool = False
        self.purchased_right: bool = False
        self.purchased_center: bool = False
        self.purchased_left: bool = False

        self.tool_belt: "ToolBelt" = None

        self.coins: SpriteList[Coin] = None
        self.current_coin: int = 0
        self._max_coins: int = 1
        self.coin_reload_period: float = 2.0

        self.available_coins: List[float] = [0.0, ] * self.max_coins

        self.attack_dist: float = 15.0

        self._max_items: int = 6

        self._quality_range: Tuple[int, int] = (1, 2)

        self._close_select: Tuple[int, int] = (0, 0)

        self._active_effect: "Consumable" = None

        self._attack_speed: float = 1.0
        self.attack_speed_bonus: float = 1.0

        self._damage: int = 1
        self.damage_bonus: int = 0

        self._weak_point_modifier: float = 1.0
        self.weak_point_bonus: float = 1.0

        self._last_hit: float = 0.0
        self._invulnerable_period: float = 2.5

    def reset(self):
        self.max_health: int = 6
        self.current_health: int = self.max_health

        self.max_speed: float = 75.0

        self.raw_position: Tuple[float, float] = (0.0, 0.0)
        self.velocity: Tuple[float, float] = (0.0, 0.0)
        self.knockback: Tuple[float, float] = (0.0, 0.0)

        self._invulnerable: bool = False
        self.passive: bool = False
        self.control: bool = True

        self.payed_toll: bool = False
        self.purchased_right: bool = False
        self.purchased_center: bool = False
        self.purchased_left: bool = False

        if self.tool_belt is not None:
            self.tool_belt.reset()

        self.coins: SpriteList[Coin] = SpriteList()
        self.current_coin: int = 0
        self._max_coins: int = 1
        self.coin_reload_period: float = 2.0

        self.available_coins: List[float] = [0.0, ] * self.max_coins

        self.attack_dist: float = 15.0

        self._max_items: int = 6

        self._quality_range: Tuple[int, int] = (1, 2)

        self._close_select: Tuple[int, int] = (0, 0)

        self._active_effect: "Consumable" = None

        self._attack_speed: float = 1.0
        self.attack_speed_bonus: float = 1.0

        self._damage: int = 1
        self.damage_bonus: int = 0

        self._weak_point_modifier: float = 1.0
        self.weak_point_bonus: float = 1.0

        self._last_hit: float = 0.0
        self._invulnerable_period: float = 2.5

    def can_purchase(self, cost: int):
        return SaveData.current_currency >= cost

    def purchase(self, cost: int):
        if not self.can_purchase(cost):
            return False

        SaveData.current_currency -= cost
        return True

    @property
    def currency(self):
        return SaveData.current_currency

    @currency.setter
    def currency(self, value: int):
        SaveData.current_currency = value

    def sell(self, value: int):
        SaveData.currency_gained += value
        SaveData.current_currency += value

    def sell_trowel(self):
        SaveData.trowel_collected = False
        SaveData.current_currency += 200

    @property
    def invulnerable(self):
        return self._invulnerable or Clock.length(self._last_hit) < self._invulnerable_period

    @invulnerable.setter
    def invulnerable(self, value: bool):
        self._invulnerable = value

    @property
    def damage(self):
        return ceil(self._damage + self.damage_bonus)

    @property
    def attack_speed(self):
        return self._attack_speed * self.attack_speed_bonus

    @property
    def weak_spot_bonus(self):
        return self._weak_point_modifier + self.weak_point_bonus

    def set_effect(self, effect: "Consumable"):
        if self._active_effect is not None:
            self._active_effect.resolve()

        self._active_effect = effect

    def resolve_effect(self):
        if self._active_effect is None:
            return

        if self._active_effect.duration >= 1.0:
            self._active_effect.resolve()
            self._active_effect = None

    def effect_active(self):
        return self._active_effect is not None

    @property
    def max_coins(self):
        return self._max_coins + SaveData.coin_level

    @property
    def max_items(self):
        return self._max_items + SaveData.capacity_level*2

    @property
    def quality_range(self):
        return self._quality_range[0] + SaveData.potency_level, self._quality_range[1] + SaveData.potency_level*2

    def generate_quality(self):
        return randint(self.quality_range[0], self._quality_range[1])

    def set_primary_sprite(self, sprite: Sprite):
        self.primary_sprite = sprite

    def set_hitbox(self, sprite: Sprite):
        self.hitbox = sprite

    def set_tool_belt(self, tool_belt: "ToolBelt"):
        self.tool_belt = tool_belt

    def setup_coins(self):
        self.coins = SpriteList()
        self._max_coins = 1
        self.current_coin = 0
        self.available_coins = [0.0, ] * self.max_coins

    def add_coin(self):
        SaveData.coin_level += 1
        self.available_coins.append(0.0)
        self.available_coins.sort()

    def remove_coin(self, _coin: Coin):
        self.coins.remove(_coin)

        self.available_coins[-1] = 0.0
        self.available_coins.sort()
        self.current_coin = self._max_coins - self.available_coins.count(0.0)

    def throw_coin(self):
        if self.current_coin >= len(self.available_coins):
            return False

        self.available_coins[self.current_coin] = Clock.time

        _new_coin = Coin(*self.raw_position, *WindowData.mouse_pos)
        self.coins.append(_new_coin)
        return True

    def update_coins(self):
        for coin in tuple(self.coins):
            coin.animate()
            if coin.landed or coin.collides_with_list(WindowData.game_view.current_map.walls):
                coin.remove_from_sprite_lists()

        for index, recharge in enumerate(self.available_coins):
            _t = Clock.length(recharge)
            if not recharge or _t < self.coin_reload_period:
                continue

            self.available_coins[index] = 0.0

        self.available_coins.sort()
        self.current_coin = self.max_coins - self.available_coins.count(0.0)

    def hit(self, attack: "Attack"):
        if self.invulnerable:
            return


        _damage = 1 + int(SaveData.number_of_kills * attack.damage_mod / 2)

        _dx = (PlayerData.raw_x - attack.hitbox.center_x)
        _dy = (PlayerData.raw_y - attack.hitbox.center_y)
        _dist = attack.knockback / ((_dx ** 2 + _dy ** 2) ** 0.5)
        self.knockback = (_dx * _dist, _dy * _dist)

        if self.current_health == self.max_health:
            _damage = min(_damage, self.max_health - 1)

        self.take_damage(_damage)

    def take_damage(self, damage: int):
        damage = min(damage, self.current_health)
        SaveData.damage_taken += damage

        self.current_health -= damage
        self._last_hit = Clock.time

        if self.current_health <= 0:
            WindowData.game_view.show_defeat()

    def heal(self, healing_factor: int):
        self.current_health = min(self.current_health+healing_factor, self.max_health)

    @property
    def raw_x(self):
        return self.raw_position[0]

    @property
    def raw_y(self):
        return self.raw_position[1]

    @property
    def raw_pos(self):
        return self.raw_position

    @raw_pos.setter
    def raw_pos(self, value: Tuple[float, float]):
        self.raw_position = value

        self.primary_sprite.position = int(value[0]), int(value[1])
        self.hitbox.position = int(value[0]), int(value[1])-4

        _dx, _dy = WindowData.mouse_pos[0] - value[0], WindowData.mouse_pos[1] - value[1]
        _dist = 16 / (_dx**2+_dy**2)**0.5
        _dx, _dy = _dx*_dist, _dy*_dist
        self._close_select = int((value[0]+_dx)/16) * 16 + 8, int((value[1]+_dy)/16)*16 + 8

    @property
    def select_pos(self):
        return self._close_select

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

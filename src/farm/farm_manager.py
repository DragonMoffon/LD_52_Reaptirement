from typing import Dict, Tuple
from random import choice

from arcade import Sprite, SpriteList, load_textures, Texture, load_texture

from src.farm.crop import Crop, CropData

from src.player.consumables import OblivionRoot, PetalOfArdour, Direan, BloodStem, IchorHorn
from src.farm.tools import Produce

from src.data import PlayerData, SaveData

if False:
    from src.map.game_map import GameMap


def generate_crop_data():
    _slices = ((0, 0, 16, 16), (0, 16, 16, 16))
    _textures = tuple(load_textures(":assets:/textures/tiles/crops.png", _slices))
    _icon = load_texture(":assets:/textures/UI/consumable_bag.png", x=0, y=0, width=32, height=32)
    _oblivion_root = CropData("Oblivion Root", _textures, 4.0, OblivionRoot, _icon, 5)

    _slices = ((16, 0, 16, 16), (16, 16, 16, 16), (16, 32, 16, 16))
    _textures = tuple(load_textures(":assets:/textures/tiles/crops.png", _slices))
    _icon = load_texture(":assets:/textures/UI/consumable_bag.png", x=32, y=0, width=32, height=32)
    _petal_of_ardor = CropData("Petal of Ardor", _textures, 3.0, PetalOfArdour, _icon, 5)

    _slices = ((32, 0, 16, 16), (32, 16, 16, 16), (32, 32, 16, 16))
    _textures = tuple(load_textures(":assets:/textures/tiles/crops.png", _slices))
    _icon = load_texture(":assets:/textures/UI/consumable_bag.png", x=64, y=0, width=32, height=32)
    _direan = CropData("Direan", _textures, 1.2, Direan, _icon, 5)

    _slices = ((48, 0, 16, 16), (48, 16, 16, 16), (48, 32, 16, 16))
    _textures = tuple(load_textures(":assets:/textures/tiles/crops.png", _slices))
    _icon = load_texture(":assets:/textures/UI/consumable_bag.png", x=96, y=0, width=32, height=32)
    _blood_stem = CropData("Blood Stem", _textures, 0.6, BloodStem, _icon, 5)

    _slices = ((64, 0, 16, 16), (64, 16, 16, 16))
    _textures = tuple(load_textures(":assets:/textures/tiles/crops.png", _slices))
    _icon = load_texture(":assets:/textures/UI/consumable_bag.png", x=128, y=0, width=32, height=32)
    _ichor_horn = CropData("Ichor Horn", _textures, 8.0, IchorHorn, _icon, 5)

    return _oblivion_root, _petal_of_ardor, _direan, _blood_stem, _ichor_horn


class FarmManager:
    c_crops: Tuple[CropData, CropData, CropData, CropData, CropData] = None
    c_tilled_tiles: Tuple[Texture, ...] = None
    c_watered_tiles: Tuple[Texture, ...] = None
    c_grass: Texture = None

    def __init__(self, _map: "GameMap"):
        if FarmManager.c_crops is None:
            FarmManager.c_crops = generate_crop_data()

        if FarmManager.c_tilled_tiles is None:
            _slices = ((i*16, 0, 16, 16) for i in range(4))
            FarmManager.c_tilled_tiles = tuple(load_textures(":assets:/textures/tiles/tilled_tiles.png", _slices))
            _slices = ((i*16, 16, 16, 16) for i in range(4))
            FarmManager.c_watered_tiles = tuple(load_textures(":assets:/textures/tiles/tilled_tiles.png", _slices))
            FarmManager.c_grass = load_texture(":assets:/textures/tiles/plain_grass.png")

        self._map: "GameMap" = _map

        self._crops: SpriteList = _map.decorations
        self._crop_points: Dict[Tuple[int, int], Crop] = dict()
        self._tilled_points: Dict[Tuple[int, int], Sprite] = dict()

    def update(self):
        for crop in self._crops:
            _growth = crop.grow()
            if _growth:
                _tile = crop.parent
                _index = FarmManager.c_watered_tiles.index(_tile.texture)
                _tile.texture = FarmManager.c_tilled_tiles[_index]

    def draw(self):
        self._crops.draw()

    def try_dig(self, point_sprite: Sprite):
        _point = int(point_sprite.center_x/16), int(point_sprite.center_y/16)
        if not self.can_till(point_sprite):
            return False

        _tiles = self._map.get_till_at_point(point_sprite)
        if not _tiles:
            return False

        self._tilled_points[_point] = _tiles[0]
        _tiles[0].texture = choice(FarmManager.c_tilled_tiles)
        return True

    def try_plant(self, point_sprite: Sprite, _crop_data: CropData):
        _point = int(point_sprite.center_x/16), int(point_sprite.center_y/16)
        if not self.can_plant(point_sprite):
            return False

        _crop = Crop(_crop_data, _point, self._tilled_points[_point])
        self._crop_points[_point] = _crop
        self._crops.append(_crop)

        return True

    def try_water(self, point_sprite: Sprite):
        _point = int(point_sprite.center_x / 16), int(point_sprite.center_y / 16)
        if not self.can_water(point_sprite):
            return False

        self._crop_points[_point].water()

        if self._crop_points[_point].watered:
            _index = FarmManager.c_tilled_tiles.index(self._tilled_points[_point].texture)
            self._tilled_points[_point].texture = FarmManager.c_watered_tiles[_index]

        return True

    def try_harvest(self, point_sprite: Sprite):
        _point = int(point_sprite.center_x / 16), int(point_sprite.center_y / 16)
        if not self.can_harvest(point_sprite):
            return False

        _crop = self._crop_points.pop(_point)
        _tile = self._tilled_points.pop(_point)
        _produce = _crop.produce(PlayerData.generate_quality())

        PlayerData.tool_belt.add_tool(Produce(_produce))

        _crop.remove_from_sprite_lists()
        _tile.texture = FarmManager.c_grass

        SaveData.crops_harvested += 1

        return True

    def can_till(self, point_sprite: Sprite):
        _point = int(point_sprite.center_x / 16), int(point_sprite.center_y / 16)
        return _point not in self._crop_points and _point not in self._tilled_points

    def can_plant(self, point_sprite: Sprite):
        _point = int(point_sprite.center_x / 16), int(point_sprite.center_y / 16)
        return _point not in self._crop_points and _point in self._tilled_points

    def can_water(self, point_sprite: Sprite):
        _point = int(point_sprite.center_x / 16), int(point_sprite.center_y / 16)
        return _point in self._crop_points and not self._crop_points[_point].watered

    def can_harvest(self, point_sprite: Sprite):
        _point = int(point_sprite.center_x / 16), int(point_sprite.center_y / 16)
        return _point in self._crop_points and self._crop_points[_point].grown and PlayerData.tool_belt.space()



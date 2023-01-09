from typing import Dict, Tuple

from arcade import SpriteList, Sprite, Texture, TileMap, load_tilemap
from pyglet.math import Vec2

from src.map.dynamics import DynamicFarmInteractables, DynamicStoreInteractables, DynamicArenaInteractables, Dynamic

from src.data import WindowData


def load_maps():
    _farm_src = ":assets:/tiled/farm/Farm.tmx"
    _store_src = ":assets:/tiled/crypts/Store.tmx"
    _arena_src = ":assets:/tiled/crypts/Arena.tmx"

    _farm = GameMap.from_tiled_map(load_tilemap(_farm_src,
                                                use_spatial_hash=True, offset=Vec2(0.0, 0.0)),
                                   DynamicFarmInteractables((0.0, 0.0)))
    _store_offset = Vec2(_farm.bounds[2], 0.0)
    _store = GameMap.from_tiled_map(load_tilemap(_store_src,
                                                 use_spatial_hash=True, offset=_store_offset),
                                    DynamicStoreInteractables(tuple(_store_offset)))
    _arena_offset = Vec2(_store.bounds[2], -160.0)
    _arena_src = GameMap.from_tiled_map(load_tilemap(_arena_src,
                                                     use_spatial_hash=True, offset=_arena_offset),
                                        DynamicArenaInteractables(tuple(_arena_offset)))

    return _farm, _store, _arena_src


class GameMap:

    def __init__(self,
                 ground: SpriteList,
                 walls: SpriteList,
                 till: SpriteList,
                 interactables: Dynamic,
                 decorations: SpriteList,
                 decorations_by_pos: Dict[Tuple[int, int], Sprite],
                 offset: Tuple[float, float],
                 size: Tuple[float, float]):
        self.ground = ground
        self.walls = walls
        self.till = till
        self.decorations = decorations

        self.decorations_by_pos: Dict[Tuple[int, int], Sprite] = decorations_by_pos

        self.interactables = interactables

        self._offset = offset
        self._size = size

    @property
    def bounds(self):
        return self._offset[0], self._offset[1], self._offset[0]+self._size[0], self._offset[1]+self._size[1]

    @staticmethod
    def from_tiled_map(_map: TileMap, dynamic_interactibles: Dynamic):
        _ground = _map.sprite_lists['floor']
        _walls = _map.sprite_lists['walls']
        _till = _map.sprite_lists['till']
        _decorations = _map.sprite_lists['decorations']
        _deco_by_pos: Dict[Tuple[int, int], Sprite] = dict()

        for deco in _decorations:
            _pos = _map.get_cartesian(*deco.position)
            _deco_by_pos[(int(_pos[0]), int(_pos[1]))] = deco

        _size = _map.width * _map.tile_width, _map.height * _map.tile_height

        return GameMap(_ground, _walls, _till, dynamic_interactibles, _decorations, _deco_by_pos, _map.offset, _size)

    def generate(self):
        self.interactables.regenerate()

    def check_interaction(self):
        self.interactables.check_interactions()

    def update_deco_texture(self, pos: Tuple[int, int], texture: Texture):
        self.decorations_by_pos[pos].texture = texture

    def add_deco(self, pos: Tuple[int, int], sprite: Sprite):
        if pos in self.decorations_by_pos:
            raise ValueError("Attempting to place a deco where there already is one, try changing the texture instead")

        self.decorations_by_pos[pos] = sprite
        self.decorations.append(sprite)

    def get_till_at_point(self, point_sprite: Sprite):
        return point_sprite.collides_with_list(self.till)

    def collides_with_wall(self, sprite: Sprite):
        return sprite.collides_with_list(self.walls)

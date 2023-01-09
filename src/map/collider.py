from typing import Tuple

from arcade import Sprite

from src.map.game_map import GameMap


class Collider:

    def __init__(self, source):
        self._source = source
        self._old_pos: Tuple[float, float] = source.raw_pos

    def resolve_collision(self, _map: GameMap):
        if _map.collides_with_wall(self._source.hitbox):
            self._source.raw_pos = self._old_pos
            return
        self._old_pos = self._source.raw_pos

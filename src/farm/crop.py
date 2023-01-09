from typing import Tuple, NamedTuple, Type

from arcade import Sprite, Texture

from src.player.consumables import Consumable

from src.data import PlayerData

from src.clock import Clock


class CropData(NamedTuple):
    name: str
    stage_textures: Tuple[Texture]
    stage_length: float
    produce:  Type[Consumable]
    icon: Texture
    cost: int


class Crop(Sprite):

    def __init__(self, _data: CropData, _pos: Tuple[int, int], parent_tile: Sprite):
        self._data = _data
        super().__init__()
        self.parent: Sprite = parent_tile
        self.texture = _data.stage_textures[0]
        self.position = _pos[0]*16.0+8.0, _pos[1]*16.0+8.0

        self.pos = _pos

        self.growth_time: float = Clock.time

        self.watered: bool = False
        self.grown: bool = False
        self.stage: int = 0

    @property
    def produce(self):
        return self._data.produce

    def water(self):
        if not self.watered and not self.grown:
            self.watered = True
            self.growth_time = Clock.time

    def grow(self):
        if self.watered and not self.grown:
            _t = Clock.length(self.growth_time) / self._data.stage_length
            if _t >= 1.0:
                if self.stage + 1 >= len(self._data.stage_textures) - 1:
                    self.grown = True
                self.stage += 1
                self.texture = self._data.stage_textures[self.stage]
                self.watered = False
                return True
        return False

    def hit(self):
        PlayerData.event_manager.collect_crop(self)

from typing import Tuple, Dict, List

from arcade import SpriteList, Sprite, load_texture

from src.farm.farm_manager import FarmManager
from src.farm.crop import CropData

from src.farm.tools import Tool, Trowel, WateringCan, Scythe, Produce, SeedlingBag

from src.dialog import DialogData

from src.farm.tools import SeedlingBag

from src.data import WindowData, PlayerData, SaveData


class Dynamic(SpriteList):

    def __init__(self, offset: Tuple[float, float]):
        super().__init__(use_spatial_hash=True, lazy=True)
        self._offset = offset

    def check_interactions(self):
        raise NotImplementedError()

    def regenerate(self):
        raise NotImplementedError()


class DynamicFarmInteractables(Dynamic):

    def __init__(self, offset: Tuple[float, float]):
        super().__init__(offset)
        self._store_door = Sprite(":assets:/textures/tiles/Doors1.png",
                                  center_x=offset[0]+440, center_y=offset[1]+208)
        self._store_door.hit_box = ((32.0, 64.0), (40.0, 64.0), (40.0, -48.0), (32.0, -48.0))
        self.append(self._store_door)

    def check_interactions(self):
        if self._store_door.collides_with_sprite(PlayerData.hitbox):
            WindowData.game_view.transition(WindowData.game_view.load_shop, 80.0)

    def regenerate(self):
        pass


class DynamicStoreInteractables(Dynamic):
    c_blocker_text: DialogData = None

    def __init__(self, offset: Tuple[float, float]):
        if DynamicStoreInteractables.c_blocker_text is None:
            DynamicStoreInteractables.c_blocker_text = DialogData((
                "Grim:\t\t\t\t\t\t\nI've already purchased this. The shop only restocks when I clear out Gregorio."
                "I've gotta pay the toll to do that\n\n\nPress Any Key To Continue.",
            ))

        super().__init__(offset)
        self._farm_door = Sprite(":assets:/textures/tiles/Doors2.png",
                                 center_x=offset[0]+40, center_y=offset[1]+208)
        self._farm_door.hit_box = ((-40.0, 64.0), (-32.0, 64.0), (-32.0, -48.0), (-40.0, -48.0))
        self.append(self._farm_door)

        self._arena_door = Sprite(":assets:/textures/tiles/Doors2.png",
                                  center_x=offset[0]+440, center_y=offset[1]+208)
        self._arena_door.hit_box = ((-40.0, 64.0), (-32.0, 64.0), (-32.0, -48.0), (-40.0, -48.0))
        self._arena_door.width *= -1
        self.append(self._arena_door)

        self._left_item: Sprite = Sprite(center_x=self._offset[0]+160, center_y=self._offset[1]+272)
        self._center_item: Sprite = Sprite(":assets:/textures/farms/Ferteliser.png",
                                           center_x=self._offset[0]+240, center_y=self._offset[1]+276)
        self._right_item: Sprite = Sprite(":assets:/textures/farms/BaggieBoi.png",
                                          center_x=self._offset[0]+320, center_y=self._offset[1]+276)

        self._left_blocker: Sprite = Sprite(":assets:/textures/farms/blocker.png",
                                            center_x=self._offset[0] + 160, center_y=self._offset[1] + 272)
        self._left_blocker.hit_box = ((-20.0, -20.0), (-20.0, 20.0), (20.0, 20.0), (20.0, -20.0))

        self._center_blocker: Sprite = Sprite(":assets:/textures/farms/blocker.png",
                                              center_x=self._offset[0] + 240, center_y=self._offset[1] + 276)
        self._center_blocker.hit_box = ((-20.0, -20.0), (-20.0, 20.0), (20.0, 20.0), (20.0, -20.0))

        self._right_blocker: Sprite = Sprite(":assets:/textures/farms/blocker.png",
                                             center_x=self._offset[0] + 320, center_y=self._offset[1] + 276)
        self._right_blocker.hit_box = ((-20.0, -20.0), (-20.0, 20.0), (20.0, 20.0), (20.0, -20.0))

        self._seedlings: Dict[Sprite, CropData] = None

        self._sell_booth: Sprite = None
        self._toll_booth: Sprite = None

    def check_interactions(self):
        _regenerate = False
        if self._farm_door.collides_with_sprite(PlayerData.hitbox):
            WindowData.game_view.transition(WindowData.game_view.load_farm, -80.0)
        elif self._arena_door.collides_with_sprite(PlayerData.hitbox) and PlayerData.payed_toll:
            WindowData.game_view.transition(WindowData.game_view.load_boss, 80.0)

        if not PlayerData.coins:
            return

        _coin = PlayerData.coins[0]
        _collisions = _coin.collides_with_list(self)
        if not _collisions:
            return
        PlayerData.remove_coin(_coin)

        _target = _collisions[0]
        if _target in self._seedlings:
            if not PlayerData.tool_belt.space() or not PlayerData.can_purchase(5):
                return

            _type = self._seedlings[_target]
            _bag = SeedlingBag(_type)

            SaveData.products_brought += 1

            PlayerData.tool_belt.add_tool(_bag)
            PlayerData.purchase(5)

        if _target == self._sell_booth:
            _tool = PlayerData.tool_belt.current_tool
            if isinstance(_tool, Scythe):
                _txt = (
                    "Grim:\nTHERE IS NO WAY I'M SELLING THIS\n\nARE\nYOU\nMAD?\n\nPress Any Key to Continue.",
                )
                WindowData.game_view.show_blocking_dialog(None, DialogData(_txt))
            elif isinstance(_tool, WateringCan):
                _txt = (
                    "Grim:\nAnubis Gave me this as a parting gift. I don't think they'd appreciate me getting rid of it"
                    "\n\nPress Any Key to Continue.",
                )
                WindowData.game_view.show_blocking_dialog(None, DialogData(_txt))
            elif isinstance(_tool, SeedlingBag):
                _txt = (
                    f"Grim:\nI didn't get a lick of value from this {_tool.name}.",
                )
                WindowData.game_view.show_blocking_dialog(None, DialogData(_txt))
                PlayerData.tool_belt.remove_tool(_tool)
                PlayerData.sell(5)
            elif isinstance(_tool, Trowel):
                _txt = (
                    f"Grim:\nCya Trowel!\n\n\n\n\nPress Any Key To Continue.",
                )
                WindowData.game_view.show_blocking_dialog(None, DialogData(_txt))
                PlayerData.sell_trowel()
            elif isinstance(_tool, Produce):
                _value = 10 + (_tool.equipment.potency[1] * 4)
                _txt = (
                    f"Crop: {_tool.name}, with {_tool.equipment.potency[0]} potency for {_value}"
                    f"\n{_tool.description}"
                    f"\nPress Any Key To Continue.",
                )
                WindowData.game_view.show_blocking_dialog(None, DialogData(_txt))
                PlayerData.tool_belt.remove_tool(_tool)
                PlayerData.sell(_value)

        if _target == self._toll_booth:
            _cost = SaveData.toll_cost
            if PlayerData.purchase(_cost):
                _txt = (
                    "TOLL PAYED, GOODLUCK\n~Anubis\n\n\n\nPress Any Key To Continue",
                )
                WindowData.game_view.show_blocking_dialog(None, DialogData(_txt))
                PlayerData.payed_toll = True
            else:
                _txt = (
                    f"INSUFFICIENT FUNDS, REQUIRES {_cost} GOLD\n\n\n\nPress Any Key To Continue",
                )
                WindowData.game_view.show_blocking_dialog(None, DialogData(_txt))

        if any((_target == self._left_blocker, _target == self._center_blocker, _target == self._right_blocker)):
            WindowData.game_view.show_blocking_dialog(None, DynamicStoreInteractables.c_blocker_text)
            return

        if _target == self._left_item:
            if SaveData.trowel_collected:
                _cost = 250 + SaveData.coin_level * 100
                if PlayerData.purchase(_cost):
                    _regenerate = True
                    PlayerData.purchased_left = True
                    PlayerData.add_coin()
                else:
                    _txt = (f"Grim:\nTo get another of Charon's Coins I need "
                            f"{int(_cost - PlayerData.currency)} more gold. Guess it's planting time"
                            f"\n\n\nPress Any Key To Continue",)
                    WindowData.game_view.show_blocking_dialog(None, DialogData(_txt))
                # Purchase coin for 250 + 100 * coin level
            elif PlayerData.purchase(200):
                SaveData.trowel_collected = True
                PlayerData.purchased_left = True
                _regenerate = True
            else:
                _txt = (f"Grim:\nThe Trowel costs 200 coins, I've only got {int(PlayerData.currency)}."
                        f"Need sell more crops.\n\n\n\nPress Any Key To Continue",)
                WindowData.game_view.show_blocking_dialog(None, DialogData(_txt))

        elif _target == self._center_item:
            _cost = 250 + SaveData.potency_level * 50
            if PlayerData.purchase(_cost):
                SaveData.potency_level += 1
                PlayerData.purchased_center = True
                _regenerate = True
            else:
                _txt = (
                    f"Grim:\nI've got {PlayerData.currency} but the Fertiliser costs {_cost}."
                    f"Gotta sell the crud to get the gold."
                    f"\n\n\n\nPress Any Key To Continue",
                )
                WindowData.game_view.show_blocking_dialog(None, DialogData(_txt))

        elif _target == self._right_item:
            _cost = 250 + SaveData.capacity_level * 125
            if PlayerData.purchase(_cost):
                SaveData.capacity_level += 1
                _regenerate = True
                PlayerData.purchased_right = True
            else:
                _txt = (
                    f"Grim:\n Ah how unfortunate the new bag costs {_cost} gold."
                    f" Damn my measly {PlayerData.currency} won't cut it."
                    f" Back'n'forth I go."
                    f"\n\n\nPress Any Key TO Continue",
                )
                WindowData.game_view.show_blocking_dialog(None, DialogData(_txt))

        if _regenerate:
            self.regenerate()

    def regenerate(self):
        if self._seedlings is None:
            self._seedlings = dict()
            for index, crop_type in enumerate(FarmManager.c_crops):
                _sprite = Sprite()
                _sprite.texture = crop_type.icon
                _sprite.position = int((9.5 + index*3.0) * 16 + self._offset[0]), 7.5 * 16 + self._offset[1]
                self.append(_sprite)
                self._seedlings[_sprite] = crop_type

        if self._sell_booth is None:
            self._sell_booth = Sprite(":assets:/textures/tiles/TollBooth.png")
            self._sell_booth.position = int(3 * 16 + self._offset[0]), int(16.5 * 16 + self._offset[1])

            self.append(self._sell_booth)

        if self._toll_booth is None:
            self._toll_booth = Sprite(":assets:/textures/tiles/TollBooth.png")
            self._toll_booth.position = int(27 * 16 + self._offset[0]), int(16.5 * 16 + self._offset[1])

            self.append(self._toll_booth)

        if SaveData.number_of_kills:
            if PlayerData.purchased_left :
                if self._left_blocker not in self:
                    self.append(self._left_blocker)
            elif self._left_blocker in self:
                self.remove(self._left_blocker)

            if PlayerData.purchased_center:
                if self._center_blocker not in self:
                    self.append(self._center_blocker)
            elif self._center_blocker in self:
                self.remove(self._center_blocker)

            if PlayerData.purchased_right:
                if self._right_blocker not in self:
                    self.append(self._right_blocker)
            elif self._right_blocker in self:
                self.remove(self._right_blocker)

            if not SaveData.trowel_collected:
                self._left_item.texture = load_texture(":assets:/textures/player/Trowel.png")
                self._left_item.hit_box = ((-16.0, -16.0), (-16.0, 16.0), (16.0, 16.0), (16.0, -16.0))
            else:
                self._left_item.texture = load_texture(":assets:/textures/UI/CoinBucket.png")

            if self._left_item not in self:
                self.extend((self._left_item, self._center_item, self._right_item))
        elif self._left_item in self:
            self.remove(self._left_item)
            self.remove(self._center_item)
            self.remove(self._right_item)


class DynamicArenaInteractables(Dynamic):

    def __init__(self, offset: Tuple[float, float]):
        super().__init__(offset)
        self._offset = offset
        self._store_door = Sprite(":assets:/textures/tiles/Doors2.png",
                                  center_x=offset[0] + 40, center_y=offset[1] + 368)
        self._store_door.hit_box = ((-40.0, 64.0), (-32.0, 64.0), (-32.0, -48.0), (-40.0, -48.0))
        self.append(self._store_door)

    def check_interactions(self):
        pass

    def regenerate(self):
        pass

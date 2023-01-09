from typing import List, NamedTuple

from arcade import SpriteList, Texture, load_texture, SpriteSolidColor

from src.player.consumables import Consumable
from src.farm.crop import CropData

from src.player.coin import Coin

from src.combat.player_weapons import PlayerScythe, PlayerTrowel, PlayerWateringCan


from src.data import PlayerData, WindowData, SaveData


class Tool:
    c_pointer: SpriteSolidColor = None

    def __init__(self, _equipment: any, _name: str, _description: str, _icon: Texture):
        if Tool.c_pointer is None:
            Tool.c_pointer = SpriteSolidColor(1, 1, (255, 255, 255))

        self._name: str = _name
        self._description: str = _description
        self._equipment: any = _equipment

        self.icon: Texture = _icon

    def show_tool(self):
        pass

    def hide_tool(self):
        pass

    def sell(self):
        pass

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def equipment(self):
        return self._equipment

    def update(self):
        raise NotImplementedError()

    def right_click(self):
        raise NotImplementedError()

    def right_release(self):
        raise NotImplementedError()

    def left_click(self):
        raise NotImplementedError()

    def left_release(self):
        raise NotImplementedError()


class Scythe(Tool):

    def __init__(self, weapon: PlayerScythe):
        super().__init__(weapon, "Scythe",
                         """Your trusty companion. Effective soul slaying capabilities,
                         and a rather poor digging implement. The perfect farming tool""",
                         load_texture(":assets:/textures/player/Scythe.png"))

    def show_tool(self):
        self._equipment.show_weapon()

    def hide_tool(self):
        self._equipment.hide_weapon()

    def update(self):
        self._equipment.update()

    def right_click(self):
        pass

    def right_release(self):
        self._equipment.throw_coin()

    def left_click(self):
        pass

    def left_release(self):
        if PlayerData.passive:
            self._equipment.farm()
            return
        self._equipment.swing()


class Trowel(Tool):

    def __init__(self, weapon: PlayerTrowel):
        super().__init__(weapon, "Trowel",
                         """Described as 'a farmer must have' all you see is an excellent soul piercing weapon.
                          Absolutely to use in the garden.""",
                         load_texture(":assets:/textures/player/Trowel.png"))

    def show_tool(self):
        self._equipment.show_weapon()

    def hide_tool(self):
        self._equipment.hide_weapon()

    def update(self):
        self._equipment.update()

    def right_click(self):
        pass

    def right_release(self):
        self._equipment.throw_coin()

    def left_click(self):
        pass

    def left_release(self):
        if PlayerData.passive:
            return

        self._equipment.swing()


class WateringCan(Tool):

    def __init__(self, watering_can):
        super().__init__(watering_can, "Soul Can",
                         """An infinite well of Hell's worst inhabitants, guilt free plant nourishment! 
                         In a nifty container and everything.""",
                         load_texture(":assets:/textures/player/WateringCan.png"))

    def show_tool(self):
        self._equipment.show_weapon()

    def hide_tool(self):
        self._equipment.hide_weapon()

    def update(self):
        self._equipment.update()

    def right_click(self):
        pass

    def right_release(self):
        self._equipment.throw_coin()

    def left_click(self):
        pass

    def left_release(self):
        self._equipment.water()


class SeedlingBag(Tool):

    def __init__(self, data: CropData):
        super().__init__(data, f"Seedling of {data.name}",
                         f"""High quality seedling straight from the depths of Hell""",
                         data.icon)

    def update(self):
        _dx, _dy = WindowData.mouse_pos[0] - PlayerData.raw_x, WindowData.mouse_pos[1] - PlayerData.raw_y
        _dist = 16 / ((_dx**2+_dy**2)**0.5 or 1)
        _dx, _dy = _dx * _dist, _dy * _dist
        Tool.c_pointer.position = PlayerData.select_pos

    def right_click(self):
        pass

    def right_release(self):
        PlayerData.throw_coin()

    def left_click(self):
        pass

    def left_release(self):
        print(self.c_pointer.position)
        _planted = WindowData.game_view.try_plant(self.c_pointer, self._equipment)
        print(_planted)
        if _planted:
            PlayerData.tool_belt.remove_tool(self)


class Produce(Tool):

    def __init__(self, consumable: Consumable):
        super().__init__(consumable, consumable.c_name, consumable.c_description, consumable.c_icon)

    def update(self):
        pass

    def right_click(self):
        pass

    def right_release(self):
        PlayerData.throw_coin()

    def left_click(self):
        pass

    def left_release(self):
        if PlayerData.effect_active() or not self._equipment.should_use():
            return

        SaveData.crops_consumed += 1

        self._equipment.use()
        PlayerData.tool_belt.remove_tool(self)


class SetTools(NamedTuple):
    scythe: Scythe
    trowel: Trowel
    watering_can: WateringCan


class CombatTools(NamedTuple):
    scythe: Scythe
    trowel: Trowel


class ToolBelt:

    def __init__(self, renderer: SpriteList):
        self._renderer = renderer
        self._set_tools: SetTools = SetTools(Scythe(PlayerScythe(renderer)),
                                             Trowel(PlayerTrowel(renderer)),
                                             WateringCan(PlayerWateringCan(renderer)))

        self._combat_tools: CombatTools = CombatTools(self._set_tools.scythe, self._set_tools.trowel)

        self._dynamic_tools: List[Tool] = []

        self._current_tool: int = 0
        self.current_tool.show_tool()

    @property
    def tools(self) -> List[Tool]:
        _trowel = [self._set_tools.trowel] if SaveData.trowel_collected else []
        if PlayerData.passive:

            _tools = [self._set_tools.scythe, self._set_tools.watering_can] + _trowel
            return _tools + self._dynamic_tools
        return [self._set_tools.scythe] + _trowel + self._dynamic_tools

    @property
    def current_tool(self) -> Tool:
        _tools = self.tools
        self._current_tool = min(len(_tools), self._current_tool)
        return _tools[self._current_tool]

    def reset(self):
        self._dynamic_tools = []
        self.current_tool.hide_tool()
        self._current_tool = 0
        self.current_tool.show_tool()

    def space(self):
        return len(self._dynamic_tools) < PlayerData.max_items

    def add_tool(self, tool: Tool):
        self._dynamic_tools.append(tool)

    def remove_tool(self, tool: Tool):
        self.current_tool.hide_tool()
        self._dynamic_tools.remove(tool)
        self._current_tool = max(0, self._current_tool-1)
        self.current_tool.show_tool()

    def scroll_tools(self, _dir: int):
        _tools = self.tools
        self.current_tool.hide_tool()
        self._current_tool = (self._current_tool-_dir) % len(_tools)
        self.current_tool.show_tool()

    def adjacent_tools(self, _dir: int):
        _tools = self.tools
        return _tools[(self._current_tool+_dir) % len(_tools)]

    def update(self):
        self.current_tool.update()

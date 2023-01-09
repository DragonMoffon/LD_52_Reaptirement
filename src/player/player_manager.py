from typing import Tuple
from math import copysign

from arcade import SpriteList, Sprite, MOUSE_BUTTON_RIGHT, MOUSE_BUTTON_LEFT

from src.player.movement import Movement
from src.player.animations import PlayerAnimator

from src.farm.tools import ToolBelt

from src.data import PlayerData, WindowData


class PlayerManager:

    def __init__(self,):
        self._sprite_renderer = SpriteList()

        self._sprite = Sprite()
        PlayerData.set_primary_sprite(self._sprite)

        self._tools: ToolBelt = ToolBelt(self._sprite_renderer)
        PlayerData.set_tool_belt(self._tools)

        self._crosshair_sprite = Sprite(":assets:/textures/player/crosshair.png")
        self._point_sprite = Sprite(":assets:/textures/player/crosshair_follow.png")
        self._indicator_sprite = Sprite(":assets:/textures/player/PlayerIndicator.png")
        PlayerData.set_hitbox(self._indicator_sprite)

        self._sprite_renderer.extend((self._sprite, self._crosshair_sprite, self._indicator_sprite, self._point_sprite))

        self._movement = Movement(self._sprite)
        self._animator = PlayerAnimator(self._sprite)

    @property
    def tools(self) -> ToolBelt:
        return self._tools

    @property
    def passive(self):
        return PlayerData.passive

    @passive.setter
    def passive(self, value: bool):
        PlayerData.passive = value

        if value:
            self._point_sprite.alpha = 255
            self._crosshair_sprite.alpha = 255
        else:
            self._crosshair_sprite.alpha = 255
            self._point_sprite.alpha = 0

    def update(self):
        self._movement.update()
        self._tools.update()

        self._crosshair_sprite.position = WindowData.mouse_pos

        if self.passive:
            self._point_sprite.position = PlayerData.select_pos
            self._point_sprite.color = (255, 255, 255)
            _p = WindowData.game_view.can_till(self._point_sprite)
            if _p:
                self._point_sprite.color = (140, 255, 155)

        self._indicator_sprite.position = PlayerData.pos[0], PlayerData.pos[1] - 4
        self._sprite.width = copysign(self._sprite.width, WindowData.mouse_pos[0]-PlayerData.raw_x)

        self._animator.animate()
        self._sprite_renderer.sort(key=lambda s: s.center_y)

    def draw(self):
        self._sprite_renderer.draw(pixelated=True)

    def on_key_press(self, symbol, modifiers):
        self._movement.key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        self._movement.key_release(symbol, modifiers)

    def on_mouse_press(self, button):
        if button == MOUSE_BUTTON_RIGHT:
            self._tools.current_tool.right_click()
        elif button == MOUSE_BUTTON_LEFT:
            self._tools.current_tool.left_click()

    def on_mouse_release(self, button):
        if button == MOUSE_BUTTON_RIGHT:
            self._tools.current_tool.right_release()
        if button == MOUSE_BUTTON_LEFT:
            self._tools.current_tool.left_release()

    def on_mouse_scroll(self, _dir: int):
        self._tools.scroll_tools(_dir)



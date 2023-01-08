from math import copysign

from arcade import Sprite, SpriteList, Camera, MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT

from src.player.sprite import PlayerBossSprite
from src.combat.player_weapons import PlayerScythe
from src.player.animations import PlayerAnimator
from src.player.movement import Movement

from src.player.event_manager import PlayerEventManager
from src.player.data import PlayerData
from src.data import WindowData


class PlayerBoss:

    def __init__(self):
        self._sprite_renderer = SpriteList()

        PlayerData.set_primary_sprite(self._sprite)

        self._weapon = PlayerScythe(self._sprite_renderer)

        self._crosshair_sprite = Sprite(":assets:/textures/player/crosshair.png")
        self._indicator_sprite = Sprite(":assets:/textures/player/PlayerIndicator.png")
        PlayerData.set_hitbox(self._indicator_sprite)

        self._animator = PlayerAnimator(self._sprite)

        self._movement = Movement(self._sprite)

        self._sprite_renderer.extend((self._sprite, self._weapon.sprite,
                                      self._crosshair_sprite, self._indicator_sprite))

        self._event_manager = PlayerEventManager()
        PlayerData.set_event_manager(self._event_manager)

        self._camera = Camera(viewport=WindowData.scaled_viewport,
                              projection=WindowData.scaled_projection)

    def update(self):
        self._movement.update()
        self._weapon.update()

        self._event_manager.update()

        self._crosshair_sprite.position = WindowData.mouse_pos
        self._indicator_sprite.position = PlayerData.pos[0], PlayerData.pos[1] - 4
        self._sprite.width = copysign(self._sprite.width, WindowData.mouse_pos[0]-PlayerData.raw_x)

        self._animator.animate()
        self._sprite_renderer.sort(key=lambda s: s.center_y)

    def draw(self):
        self._camera.use()
        self._sprite_renderer.draw(pixelated=True)

    def on_key_press(self, symbol, modifiers):
        self._movement.key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        self._movement.key_release(symbol, modifiers)

    def on_mouse_press(self, button):
        if button == MOUSE_BUTTON_RIGHT:
            self._weapon.throw_coin()

    def on_mouse_release(self, button):
        if button == MOUSE_BUTTON_LEFT:
            self._weapon.swing()

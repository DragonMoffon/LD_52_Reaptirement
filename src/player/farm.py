from arcade import Sprite, SpriteList, Camera

from src.player.sprite import PlayerFarmSprite
from src.player.movement import Movement
from src.player.data import PlayerData

from src.data import WindowData


class PlayerFarm:

    def __init__(self):
        self._sprite_renderer = SpriteList()

        self._sprite = PlayerFarmSprite()
        self._sprite_renderer.append(self._sprite)

        self._crosshair_sprite = Sprite(":assets:/textures/player/crosshair.png")
        self._sprite_renderer.append(self._crosshair_sprite)

        self._movement = Movement(self._sprite)

        self._camera = Camera(viewport=WindowData.scaled_viewport,
                              projection=WindowData.scaled_projection)

    def update(self):
        self._movement.update()
        self._crosshair_sprite.position = WindowData.mouse_pos

    def draw(self):
        self._camera.use()
        self._sprite_renderer.draw(pixelated=True)

    def on_key_press(self, symbol, modifiers):
        self._movement.key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        self._movement.key_release(symbol, modifiers)

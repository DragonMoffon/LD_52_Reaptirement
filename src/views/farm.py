from arcade import View
from arcade.tilemap import TileMap

from src.clock import Clock

from src.player.farm import PlayerFarm


class FarmView(View):

    def __init__(self):
        super().__init__()
        self.player: PlayerFarm = None
        self.map: TileMap = TileMap(":assets:/tiled/test.tmx", use_spatial_hash=True)

    def on_update(self, delta_time: float):
        Clock.tick(delta_time)
        self.player.update()

    def on_draw(self):
        Clock.frame_tick()
        self.clear()
        with self.window.low_res_fbo.activate():
            self.window.low_res_fbo.clear()
            self.map.sprite_lists['ground'].draw(pixelated=True)
            self.map.sprite_lists['decorations'].draw(pixelated=True)
            self.player.draw()

    def on_show_view(self):
        self.window.set_mouse_visible(False)
        self.player = PlayerFarm()

    def on_hide_view(self):
        self.window.set_mouse_visible(True)

    def on_key_press(self, symbol: int, modifiers: int):
        self.player.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        self.player.on_key_release(symbol, modifiers)

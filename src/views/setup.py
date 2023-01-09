from math import floor, sin, pi

from arcade import View, get_display_size, Sprite, load_texture, draw_point

from src.low_res_fbo import LowResFBO
from src.data import WindowData

from src.clock import Clock


class SetupView(View):

    def __init__(self):
        super().__init__()
        self.window.set_fullscreen(True)
        self._splash_sprite = Sprite(":assets:/textures/arcade-logo-splash.png",
                                     center_x=self.window.width//2,
                                     center_y=self.window.height//2)
        self._splash_sprite.alpha = 0

    def on_update(self, delta_time: float):
        Clock.tick(delta_time)
        if Clock.frame - 512 < 512:
            self._splash_sprite.alpha = sin(pi * Clock.frame / 512)**2 * 255
        else:
            self._generate_fbo()
            self.window.start_game()
        if Clock.frame == 512:
            self._splash_sprite.texture = load_texture(":assets:/textures/dragon-bakery-splash.png")

    def _generate_fbo(self):
        _screen_resolution = get_display_size()
        _down_scaled_resolution = (480, 270)
        _up_scale_multiplier = floor(_screen_resolution[0]/_down_scaled_resolution[0])

        WindowData.set_resolution_data(_screen_resolution, _down_scaled_resolution, _up_scale_multiplier)
        _fbo = LowResFBO(self.window.ctx, size=_down_scaled_resolution)
        self.window.low_res_fbo = _fbo

    def on_show_view(self):
        Clock.tick_speed = 0.0

    def on_hide_view(self):
        Clock.tick_speed = 1.0

    def on_draw(self):
        self.clear()
        if Clock.frame - 512 < 512:
            self._splash_sprite.draw(pixelated=True)



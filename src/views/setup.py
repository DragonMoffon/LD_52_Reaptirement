from math import floor

from arcade import View, get_display_size

from src.low_res_fbo import LowResFBO
from src.data import WindowData


class SetupView(View):

    def __init__(self):
        super().__init__()

    def on_key_press(self, symbol: int, modifiers: int):
        self._generate_fbo()
        self.window.show_boss_view()

    def _generate_fbo(self):
        _screen_resolution = get_display_size()
        _down_scaled_resolution = (480, 270)
        _up_scale_multiplier = floor(_screen_resolution[0]/_down_scaled_resolution[0])

        WindowData.set_resolution_data(_screen_resolution, _down_scaled_resolution, _up_scale_multiplier)
        _fbo = LowResFBO(self.window.ctx, size=_down_scaled_resolution)
        self.window.low_res_fbo = _fbo

    def on_hide_view(self):
        self.window.set_fullscreen(True)

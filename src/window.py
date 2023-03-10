from arcade import Window, get_display_size
from arcade.key import ESCAPE

from src.views.game import GameView

from src.views.setup import SetupView

from src.low_res_fbo import LowResFBO

from src.data import WindowData
from src.vignette import set_vignette


class AppWindow(Window):

    def __init__(self):
        _screen_size = get_display_size()
        super().__init__(width=480, height=270, title="Reaptirement: a LD 52 game",
                         fullscreen=False, update_rate=1/120, vsync=True)
        WindowData.set_window()
        self.low_res_fbo: LowResFBO = None
        set_vignette()

        _setup_view = SetupView()
        self.show_view(_setup_view)

        self.game_view = GameView()

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        WindowData.true_mouse_position = (x, y)

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        WindowData.true_mouse_position = (x, y)

    def on_mouse_enter(self, x: int, y: int):
        WindowData.true_mouse_position = (x, y)

    def on_mouse_leave(self, x: int, y: int):
        WindowData.true_mouse_position = (x, y)

    def start_game(self):
        self.game_view.begin_game()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == ESCAPE:
            self.close()

    def on_update(self, delta_time: float):
        pass

    def on_draw(self):
        if not isinstance(self.current_view, SetupView):
            self.clear()

        if self.low_res_fbo:
            self.low_res_fbo.draw()

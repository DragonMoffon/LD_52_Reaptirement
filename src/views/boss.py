from arcade import View

from src.clock import Clock

from src.player.boss import PlayerBoss

from src.enemies.boss import BossManager

from src.combat.combat import CombatManager

from src.data import WindowData


class BossView(View):

    def __init__(self):
        super().__init__()
        self.player: PlayerBoss = None
        self.boss_manager: BossManager = None
        self.combat_manager: CombatManager = None

    def on_update(self, delta_time: float):
        Clock.tick(delta_time)
        self.player.update()
        self.boss_manager.update()
        self.combat_manager.update()

    def on_draw(self):
        Clock.frame_tick()
        self.clear()
        with self.window.low_res_fbo.activate():
            self.window.low_res_fbo.clear()
            self.player.draw()
            self.boss_manager.draw()
            self.combat_manager.draw()

            WindowData.camera.use()
            WindowData.vignette.draw(pixelated=True)

    def on_show_view(self):
        self.window.set_mouse_visible(False)
        self.player = PlayerBoss()

        self.boss_manager = BossManager()

        self.combat_manager = CombatManager()

        _hb, _ws, _em = self.boss_manager.generate_georgie()
        self.combat_manager.set_enemy(_hb, _em)
        self.combat_manager.set_weakspot(_ws)

    def on_hide_view(self):
        self.window.set_mouse_visible(True)

    def on_key_press(self, symbol: int, modifiers: int):
        self.player.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        self.player.on_key_release(symbol, modifiers)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        self.player.on_mouse_press(button)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        self.player.on_mouse_release(button)

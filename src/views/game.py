from math import cos, pi

from arcade import View, SpriteSolidColor, Sprite, lerp

from src.player.player_manager import PlayerManager

from src.combat.boss import BossManager

from src.combat.combat import CombatManager

from src.farm.farm_manager import FarmManager

from src.ui import UiManager

from src.map.game_map import load_maps, GameMap
from src.map.collider import Collider

from src.clock import Clock

from src.dialog import Dialog, DialogData

from src.views.lose_win import WinView, LoseView

from src.data import WindowData, PlayerData, SaveData


class GameView(View):
    c_starting_dialog: DialogData = None

    c_transition_speed: float = 1.6

    def __init__(self):
        if GameView.c_starting_dialog is None:
            GameView.c_starting_dialog = DialogData((
             "Hey Grim! Bummer big boss fired you like that. With the humans dead I suppose it was inevitable."
             "Why don't you take up farming? Have my old watering can\n ~Anubis"
             "\n\nPress Anything To Continue.",
             "Charon:\n Hey Grim, Boss got rid of me too. Here take my coin."
             " you can dash by right clicking and then left clicking towards the coin (while holding the Scythe)."
             "\n\nPress Anything To Continue.",
             "Grim if you pay the toll you can clean up the souls leaking out of hell."
             "The shop can replenish once you do, Just head to the right. Anyway cya Grim!\n~Anubis"
             "\n\nPress Anything To Continue.",
             "Charon:\nI'm going fishing see you around Grim."
             "\n\nPress Anything To Continue.",
             "Move with W,A,S,D interact with stuff by throwing a coin (RMB)"
             " use your currently selected tool using (LMB). press ESCAPE to close the game\n"
             "\n\nPress Anything To Continue."
            ))

        super().__init__()
        WindowData.set_game_view(self)

        # TODO: Player Section

        self._player: PlayerManager = None

        self._player_collider: Collider = None

        PlayerData.setup_coins()

        # Player object with weapon, inventory, sprites, and animations

        # TODO: Enemy Section

        self._boss_manager: BossManager = None
        self.combat_manager: CombatManager = None

        # TODO: Map Section

        self._current_map: GameMap = None
        self._farm: GameMap = None
        self._store: GameMap = None
        self._arena: GameMap = None

        # TODO: Farm Section

        self._farm_manager: FarmManager = None

        self._ui_manager: UiManager = UiManager()

        # Contains an inventory of all the plants currently growing

        self._transitioning: bool = False
        self._transition_dist: float = 0.0
        self._transition_start: float = 0.0
        self._transition_function: () = None
        self._transition_cover: SpriteSolidColor = SpriteSolidColor(WindowData.down_scale_resolution[0],
                                                                    WindowData.down_scale_resolution[1],
                                                                    (0, 0, 0, 255))
        self._transition_cover.position = WindowData.down_scale_resolution[0]//2, WindowData.down_scale_resolution[1]//2
        self._transition_cover.alpha = 0

        self._blocking_dialog: Dialog = None

    @property
    def boss_manager(self):
        return self._boss_manager

    def show_blocking_dialog(self, call_back, data: DialogData):
        _old_tick_speed = Clock.tick_speed

        def hide_blocking_dialog():
            Clock.tick_speed = _old_tick_speed
            PlayerData.control = True
            self._blocking_dialog = None
            if call_back is not None:
                call_back()

        Clock.tick_speed = 0
        PlayerData.control = False
        self._blocking_dialog = Dialog(hide_blocking_dialog, data)
        return self._blocking_dialog

    def on_update(self, delta_time):
        Clock.tick(delta_time)
        if not self._transitioning:
            self._player.update()
            self._player_collider.resolve_collision(self._current_map)

            self._current_map.check_interaction()

            self._boss_manager.update()

            self.combat_manager.update()
            self._farm_manager.update()

            PlayerData.update_coins()
            PlayerData.resolve_effect()

        else:
            _t = max(min(Clock.length(self._transition_start) / self.c_transition_speed, 1.0), 0.0)
            if _t >= 0.5 and self._transition_function:
                self._transition_function()
                self._transition_function = None

                self._transition_dist = 0.0
            elif _t >= 1.0:
                self._transitioning = False
                self._transition_start = 0.0
                self._transition_cover.alpha = 0

                PlayerData.control = True
            else:
                _t = -cos(_t * 2.0*pi) * 0.5 + 0.5

                self._transition_cover.alpha = int(_t * 255)

                _speed = self._transition_dist / self.c_transition_speed
                _x = PlayerData.raw_x + _speed * Clock.delta_time

                PlayerData.raw_pos = _x, PlayerData.raw_y

        self._ui_manager.update()

        _res = WindowData.down_scale_resolution
        _camera_target_pos = PlayerData.pos[0] - _res[0]//2, PlayerData.pos[1] - _res[1]//2
        _bounds = self._current_map.bounds

        _camera_target_x = min(max(_camera_target_pos[0], _bounds[0]), _bounds[2]-_res[0])
        _camera_target_y = min(max(_camera_target_pos[1], _bounds[1]), _bounds[3]-_res[1])

        WindowData.tracked_camera.move_to((_camera_target_x, _camera_target_y), 0.6)

    def on_draw(self):
        self.clear()
        with self.window.low_res_fbo.activate():
            WindowData.tracked_camera.use()
            self.window.low_res_fbo.clear()

            self._current_map.ground.draw(pixelated=True)
            self._current_map.till.draw(pixelated=True)

            self._current_map.walls.draw(pixelated=True)
            self._current_map.decorations.draw(pixelated=True)

            self.combat_manager.draw()

            self._boss_manager.draw()
            self._player.draw()

            PlayerData.coins.draw(pixelated=True)

            self._current_map.interactables.draw(pixelated=True)

            WindowData.locked_camera.use()

            WindowData.vignette.draw(pixelated=True)

            self._ui_manager.draw()

            if self._transitioning:
                self._transition_cover.draw(pixelated=True)

            if self._blocking_dialog:
                self._blocking_dialog.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        if self._blocking_dialog is not None:
            self._blocking_dialog.press()
            return

        self._player.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        self._player.on_key_release(symbol, modifiers)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        self._player.on_mouse_press(button)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if self._blocking_dialog is not None:
            self._blocking_dialog.press()
            return
        self._player.on_mouse_release(button)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        _dir = int(scroll_y/abs(scroll_y))
        self._player.on_mouse_scroll(_dir)

    # LOADING FUNCTIONS

    def begin_game(self):
        self.window.set_mouse_visible(False)

        PlayerData.control = False
        self._transitioning = True
        self._transition_start = -self.c_transition_speed/2
        self._transition_dist = 0.0

        self._ui_manager.begin()
        self._ui_manager.hide_boss_health()

        self._farm, self._store, self._arena = load_maps()
        self._current_map = self._farm

        self._current_map.generate()

        self._boss_manager = BossManager()
        self.combat_manager = CombatManager()

        self._player = PlayerManager()
        self._player.passive = True

        PlayerData.update_coins()

        self._player_collider = Collider(PlayerData)

        self._farm_manager = FarmManager(self._farm)

        PlayerData.raw_pos = WindowData.down_scale_resolution[0]//2.0, WindowData.down_scale_resolution[1]//2.0

        self.window.show_view(self)
        self.show_blocking_dialog(None, GameView.c_starting_dialog)

    def transition(self, _func: (), dist: float = 0.0):
        PlayerData.control = False

        self._transition_dist = dist
        self._transitioning = True
        self._transition_start = Clock.time
        self._transition_function = _func

    def load_farm(self):
        self._ui_manager.hide_boss_health()

        self._current_map = self._farm
        self._current_map.generate()

        self._player.passive = True

    def load_shop(self):
        self._ui_manager.hide_boss_health()

        self._current_map = self._store
        self._current_map.generate()

        self._player.passive = True

    def load_boss(self):
        self._current_map = self._arena
        self._current_map.generate()

        self._player.passive = False

        self.combat_manager.set_walls(self._arena.walls)
        _bounds = self._arena.bounds
        _pos = lerp(_bounds[0], _bounds[2], 0.5), lerp(_bounds[1], _bounds[3], 0.5)
        self.combat_manager.set_enemy(self._boss_manager, *self._boss_manager.generate_georgie(_pos))

        self._ui_manager.show_boss_health(self._boss_manager.boss)

    def show_victory(self):
        # pause time
        # generate text
        # add rewards to player inventory
        # change View to victory View
        self._ui_manager.hide_boss_health()
        self.window.show_view(WinView())
        SaveData.save_to_file()

    def reload_player(self):
        PlayerData.control = False
        self._transitioning = True
        self._transition_start = -self.c_transition_speed / 2
        self._transition_dist = 0.0

        self.combat_manager.reset()
        self._boss_manager.reset()
        self._current_map = self._farm
        self._player.passive = True

        PlayerData.payed_toll = False
        PlayerData.purchased_right = False
        PlayerData.purchased_center = False
        PlayerData.purchased_left = False

        PlayerData.raw_pos = WindowData.down_scale_resolution[0]//2.0, WindowData.down_scale_resolution[1]//2.0

        self.window.show_view(self)

    def restart_game(self):
        PlayerData.control = False
        self._transitioning = True
        self._transition_start = -self.c_transition_speed / 2
        self._transition_dist = 0.0

        WindowData.reset()
        PlayerData.reset()

        self.begin_game()

    def show_defeat(self):
        # pause time
        # generate text
        # change View to lose View
        self._ui_manager.hide_boss_health()
        self.window.show_view(LoseView())
        SaveData.reset_save()

    def current_tool(self):
        return self._player.tools.current_tool

    def adjacent_tool(self, _dir: int):
        return self._player.tools.adjacent_tools(_dir)

    def try_dig(self, point_sprite: Sprite):
        self._farm_manager.try_dig(point_sprite)

    def try_plant(self, point_sprite: Sprite, _data):
        return self._farm_manager.try_plant(point_sprite, _data)

    def try_water(self, point_sprite: Sprite):
        self._farm_manager.try_water(point_sprite)

    def try_harvest(self, point_sprite: Sprite):
        self._farm_manager.try_harvest(point_sprite)

    def can_till(self, point_sprite: Sprite):
        return self._farm_manager.can_till(point_sprite)

    @property
    def current_map(self):
        return self._current_map

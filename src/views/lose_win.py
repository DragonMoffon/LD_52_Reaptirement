from arcade import View

from src.dialog import Dialog, DialogData

from src.data import PlayerData, WindowData, SaveData

from src.clock import Clock


class WinView(View):

    def __init__(self):
        super().__init__()
        _time = Clock.raw_length(SaveData.last_victory)
        _minutes = int(_time // 60)
        _seconds = int(_time % 60)
        _time_str = "time" if SaveData.number_of_kills == 1 else "times"
        _basic_text = [
            "Georgio the amorphous gathering of the escaped souls of hell has been defeated.\n\n"
            f"It took you\n {_minutes} m :{_seconds} s.\n" 
            f"you've killed Georgie {SaveData.number_of_kills} {_time_str}\n"
            "\nEsc to Quit\nAny to Continue",

            "Remember this game is perma-death, but if you quit on a victory screen your progress is saved.\n\n\n\n"
            "\nEsc to Quit\nAny to Continue"
        ]
        if SaveData.number_of_kills == 1:
            _basic_text.extend((
                "Congrats on your first kill! New items have been unlocked in the shop!"
                "\nEsc to Quit\nAny to Continue",

                "Firstly a Trowel for extra soul killing power, absolutely no use for farming.\n\n"
                "Fertilizer to improve the effects of produce.\n\n"
                "A larger bag so you can carry even more crap."
                "\nEsc to Quit\nAny to Continue"
            ))
        elif SaveData.number_of_kills == 3:
            _basic_text.append(
                "Thanks for playing for so long. There isn't any new content after the first run through. "
                "I hope you enjoyed yourself! It saves so keep playing!\n"
                "\nEsc to Quit\nAny to Continue"
            )

        if SaveData.trowel_collected and PlayerData.max_coins == 1:
            _basic_text.append(
                "How did you like the trowel? you can now buy extra coins instead. If you ever run out of "
                "money you can sell the trowel for an extra buck.\n"
                "\nEsc to Quit\nAny to Continue"
            )

        self._victory_data = DialogData(tuple(_basic_text))
        self.dialog = Dialog(self.reset_player, self._victory_data)
        SaveData.last_victory = Clock.raw

    def reset_player(self):
        WindowData.game_view.reload_player()

    def on_draw(self):
        with WindowData.window.low_res_fbo.activate():
            WindowData.window.low_res_fbo.clear()
            WindowData.locked_camera.use()
            PlayerData.primary_sprite.draw(pixelated=True)

            self.dialog.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        self.dialog.press()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        self.dialog.press()


class LoseView(View):
    def __init__(self):
        super().__init__()
        _time = Clock.raw
        _minutes = int(_time // 60)
        _seconds = int(_time % 60)

        _time_str = "kill" if SaveData.number_of_kills == 1 else "kills"
        _crop_str = "crop" if SaveData.crops_harvested == 1 else "crops"
        _crop_str_2 = "crop" if SaveData.crops_consumed == 1 else "crops"

        _basic_text = [
            "Georgio the amorphous gathering of the escaped souls of hell defeated you!.\n"
            "Your progress has already been deleted\n"
            f"time: {_minutes} m :{_seconds} s\n" 
            f"{SaveData.number_of_kills} {_time_str}\n"
            "\nEsc to Quit\nAny for more stats",

            f"{SaveData.currency_gained} gold earned\n"
            f"\n{SaveData.crops_harvested} {_crop_str} harvested\n"
            f"\n{SaveData.crops_consumed} {_crop_str_2} consumed\n"
            f"\n{SaveData.damage_done} damage delt\n"
            f"\n{SaveData.damage_taken} damage taken\n"
            "\nEsc to Quit\nAny to restart"
        ]

        self._lose_data = DialogData(tuple(_basic_text))
        self.dialog = Dialog(self.reset_game, self._lose_data)

    def reset_game(self):
        WindowData.game_view.restart_game()

    def on_draw(self):
        with WindowData.window.low_res_fbo.activate():
            WindowData.window.low_res_fbo.clear()
            WindowData.locked_camera.use()
            PlayerData.primary_sprite.draw(pixelated=True)

            self.dialog.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        self.dialog.press()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        self.dialog.press()

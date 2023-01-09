from arcade.resources import add_resource_handle
from arcade import load_font

from src.window import AppWindow
from src.data import SaveData


def main():
    add_resource_handle("assets", "assets")
    SaveData.load_from_file()
    load_font(":assets:/kongtext.ttf")
    app_window = AppWindow()

    app_window.run()

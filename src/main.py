from arcade.resources import add_resource_handle, resolve_resource_path

from src.window import AppWindow


def main():
    add_resource_handle("assets", "assets")
    app_window = AppWindow()
    app_window.run()

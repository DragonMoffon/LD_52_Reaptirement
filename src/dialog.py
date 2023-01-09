from typing import Tuple, List

from arcade import Sprite, Texture, load_texture, Text

from src.data import WindowData


class DialogData:

    def __init__(self, text: Tuple[str, ...]):
        _texts: List[Text] = []
        for _text_str in text:
            _text = Text(_text_str,
                         start_x=WindowData.down_scale_resolution[0]//2-104,
                         start_y=WindowData.down_scale_resolution[1]//2+48,
                         anchor_x="left", anchor_y="top", align="center",
                         width=204, multiline=True, font_name="Kongtext", font_size=6,
                         )
            _texts.append(_text)

        self.text: Tuple[Text] = tuple(_texts)
        self.current_text = 0

    def finished(self):
        return self.current_text >= len(self.text)

    def next(self):
        _this = self.text[self.current_text]
        self.current_text += 1
        return _this


class Dialog:
    c_dialog_texture: Texture = None

    def __init__(self, final_call_back, data: DialogData):
        self._call_back = final_call_back
        self._data: DialogData = data
        self._current_text: Text = self._data.next()
        if Dialog.c_dialog_texture is None:
            Dialog.c_dialog_texture = load_texture(":assets:/textures/UI/Dialogue.png")
        self._sprite = Sprite(texture=Dialog.c_dialog_texture)
        self._sprite.position = WindowData.down_scale_resolution[0]//2, WindowData.down_scale_resolution[1]//2

    def press(self):
        if self._data.finished() and self._call_back is not None:
            self._call_back()
            return

        self._current_text = self._data.next()

    def draw(self):
        self._sprite.draw(pixelated=True)
        self._current_text.draw()

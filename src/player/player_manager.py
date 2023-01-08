from arcade import View, SpriteList, Sprite


from src.data import PlayerData


class PlayerManager:

    def __init__(self, parent_view: View):
        self._parent = View

        self._sprite_renderer = SpriteList()

        self._sprite = Sprite(":assets:/textures/player/placeholder.png")



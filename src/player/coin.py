from arcade import load_textures, ease_out, lerp

from src.animated_sprite import AnimatedSprite, AnimationData

from src.clock import Clock


class Coin(AnimatedSprite):
    c_lifespan: float = 0.8
    c_frame_data: AnimationData = None

    def __init__(self, x, y, t_x, t_y):
        if Coin.c_frame_data is None:
            _slices = ((i*4, 0, 4, 4) for i in range(4))
            Coin.c_frame_data = AnimationData(tuple(load_textures(":assets:/textures/player/CoinSpin.png", _slices)),
                                              (1/32, 1/32, 1/32, 1/32), True)
        super().__init__(Coin.c_frame_data, (x, y))
        self._spawn_time: float = Clock.time

        self._target_x = t_x
        self._target_y = t_y

        self._start_x = x
        self._start_y = y

        self._raw_position = x, y
        self.position = int(x), int(y)

        self.locked = False
        self.killed = False

    @property
    def landed(self):
        return self.killed or (Clock.length(self._spawn_time) / Coin.c_lifespan >= 1.0 and not self.locked)

    def kill(self) -> None:
        self.remove_from_sprite_lists()
        self.killed = True

    def animate(self):
        if self.locked or self.killed:
            return

        _t = Clock.length(self._spawn_time) / Coin.c_lifespan

        if _t >= 1.0:
            return

        self.update_texture()

        _x = lerp(self._start_x, self._target_x, ease_out(_t))
        _y = lerp(self._start_y, self._target_y, ease_out(_t))

        self._raw_position = _x, _y
        self.position = int(_x), int(_y)
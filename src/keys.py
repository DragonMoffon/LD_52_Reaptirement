from typing import Tuple

import arcade.key as keys


class MultiKey:

    def __init__(self, values: Tuple[int, ...], str_id: str):
        self._values: Tuple[int, ...] = values
        self._str_id: str = str_id

    def __eq__(self, other):
        return any(other == v for v in self._values)


UP = keys.W  # MultiKey((keys.W, keys.UP), "up")
DOWN = keys.S  # MultiKey((keys.S, keys.DOWN), "down")
LEFT = keys.A  # MultiKey((keys.A, keys.LEFT), "left")
RIGHT = keys.D  # MultiKey((keys.D, keys.RIGHT), "right")
RSHIFT = keys.RSHIFT

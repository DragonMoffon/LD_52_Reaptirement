class _Clock:

    def __init__(self):
        self._delta_time: float = 0.0
        self._delta_tick: float = 0.0

        self._tick_speed: float = 1.0

        self._tick_time: float = 0.0
        self._raw_time: float = 0.0
        self._frame_time: int = 0.0

    def tick(self, delta_time: float):
        self._delta_tick = delta_time * self._tick_speed
        self._delta_time = delta_time

        self._tick_time += self._delta_tick
        self._raw_time += self._delta_time

        self._frame_time += 1

    def frame_tick(self):
        self._frame_time += 1

    def length(self, tick_time: float):
        return self._tick_time - tick_time

    def raw_length(self, raw_time: float):
        return self._raw_time - raw_time

    def frame_length(self, frame: int):
        return self._frame_time - frame

    @property
    def time(self):
        return self._tick_time

    @property
    def raw(self):
        return self._raw_time

    @property
    def frame(self):
        return self._frame_time

    @property
    def delta_time(self):
        return self._delta_tick

    @property
    def raw_delta_time(self):
        return self._delta_time

    @property
    def tick_speed(self):
        return self._tick_speed

    @tick_speed.setter
    def tick_speed(self, value: float):
        self._tick_speed = value


Clock = _Clock()

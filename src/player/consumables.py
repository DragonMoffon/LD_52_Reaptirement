from typing import Tuple, List, NamedTuple, Dict

from arcade import Texture, load_texture

from src.clock import Clock

from src.data import PlayerData, WindowData


class ConsumableData(NamedTuple):
    name: str
    description: str
    icon: Texture
    vignette: Tuple[float, float, float]


class Consumable:
    potency_map: Dict[int, str] = {
        1: "poor", 2: "mediocre", 3: "passable", 4: "usable", 5: "good", 6: "excellent", 7: "wonderful", 8: "powerful"
    }

    def __init__(self, _data: ConsumableData, _potency: int):
        self.c_name: str = _data.name
        self.c_description: str = _data.description
        self.c_icon: Texture = _data.icon
        self._color = _data.vignette

        self._potency: int = min(_potency, 1)

        self._started: bool = False
        self._start_time: float = 0.0
        self._duration: float = 1.0

    def should_use(self):
        return True

    @property
    def duration(self):
        _t = self._started * Clock.length(self._start_time)/self._duration
        return _t

    @property
    def potency(self):
        if self._potency >= 9:
            return "unholy", self._potency
        return Consumable.potency_map[self._potency], self._potency

    def use(self):
        raise NotImplementedError()

    def resolve(self):
        raise NotImplementedError()


class OblivionRoot(Consumable):
    c_data: ConsumableData = None

    def __init__(self, potency: int):
        if OblivionRoot.c_data is None:
            OblivionRoot.c_data = ConsumableData(
                            "Oblivion Roots",
                            "The plump bulbs of this hardy plant soak up the eons wasted away in limbo."
                            "Pull the threads of time to your will.",
                            load_texture(":assets:/textures/player/consumables.png", 0, 0, 16, 16),
                            (165, 38, 57)
                        )
        super().__init__(self.c_data, potency)

        self._slow_down: float = 0.5
        self._duration = (1.5 * potency * self._slow_down)

    def use(self):
        Clock.tick_speed -= self._slow_down
        self._started = True
        self._start_time = Clock.time

        PlayerData.set_effect(self)

        WindowData.vignette.show_vignette(self._color)

    def resolve(self):
        Clock.tick_speed += self._slow_down

        WindowData.vignette.hide_vignette()


class PetalOfArdour(Consumable):
    c_data: ConsumableData = None

    def __init__(self, potency: int):
        if PetalOfArdour.c_data is None:
            PetalOfArdour.c_data = ConsumableData(
                "Petal of Ardour",
                "The soft delectable petals of a sweet flower. Feast on endless passion to heal your cold dead heart.",
                load_texture(":assets:/textures/player/consumables.png", 16, 0, 16, 16),
                (229, 66, 134)
            )
        super().__init__(self.c_data, potency)

        self._healing_factor: int = 1 + int(potency / 3)
        self._duration: float = 2.5

    def should_use(self):
        return PlayerData.current_health != PlayerData.max_health

    def use(self):
        PlayerData.heal(self._healing_factor)
        PlayerData.set_effect(self)

        self._started = True
        self._start_time = Clock.length()

        WindowData.vignette.show_vignette(self._color)

    def resolve(self):
        WindowData.vignette.hide_vignette()


class Direan(Consumable):
    c_data: ConsumableData = None

    def __init__(self, potency: int):
        if Direan.c_data is None:
            Direan.c_data = ConsumableData(
                "D-ire-an",
                "A spikey fruit infused with the vile smell of rage and anguish."
                "Strike with the anger of long dead gods.",
                load_texture(":assets:/textures/player/consumables.png", 32, 0, 16, 16),
                (133, 76, 191)
            )
        super().__init__(self.c_data, potency)
        self._multiplier = 0.05*potency**2 + 0.95
        self._duration: float = 3.0 + potency * 0.25

    def should_use(self):
        return not PlayerData.passive

    def use(self):
        PlayerData.damage_bonus = self._multiplier
        PlayerData.set_effect(self)

        self._started = True
        self._start_time = Clock.time

        WindowData.vignette.show_vignette(self._color)

    def resolve(self):
        PlayerData.damage_bonus = 1.0

        WindowData.vignette.hide_vignette()


class BloodStem(Consumable):
    c_data: ConsumableData = None

    def __init__(self, potency: int):
        if BloodStem.c_data is None:
            BloodStem.c_data = ConsumableData(
                "Blood Stem",
                "The red and blue arteries of hell itself sprouting from the earth."
                "Swing with the frenzied speed of violence",
                load_texture(":assets:/textures/player/consumables.png", 48, 0, 16, 16),
                (114, 28, 47)
            )
        super().__init__(self.c_data, potency)
        self._multiplier = 1 / potency**0.5
        self._duration: float = 3.0 + potency * 0.5

    def use(self):
        PlayerData.attack_speed_bonus = self._multiplier
        PlayerData.set_effect(self)

        self._started = True
        self._start_time = Clock.time

        WindowData.vignette.show_vignette(self._color)

    def resolve(self):
        PlayerData.damage_bonus = 1.0

        WindowData.vignette.hide_vignette()


class IchorHorn(Consumable):
    c_data: ConsumableData = None

    def __init__(self, potency: int):
        if IchorHorn.c_data is None:
            IchorHorn.c_data = ConsumableData(
                "Ichor Horn",
                "A twisted and gnarled horn, a figment of the banished."
                "Tip your blade with the icy power of treachery.",
                load_texture(":assets:/textures/player/consumables.png", 64, 0, 16, 16),
                (140, 218, 255)
            )
        super().__init__(self.c_data, potency)
        self._multiplier = 1 + 0.02*potency**2 + 0.05*potency + 0.5
        self._duration = 2.0 + potency * 0.25

    def should_use(self):
        return not PlayerData.passive

    def use(self):
        PlayerData.weak_spot_bonus = self._multiplier
        PlayerData.set_effect(self)

        self._started = True
        self._start_time = Clock.time

        WindowData.vignette.show_vignette(self._color)

    def resolve(self):
        PlayerData.weak_spot_bonus = 1.0

        WindowData.vignette.hide_vignette()


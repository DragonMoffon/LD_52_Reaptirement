from typing import Tuple, List

from arcade import Sprite


class Consumable:

    def __init__(self, sprite: Sprite, _duration: float = 1.0, _potency: float = 1.0,
                 _vignette_color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)):
        self._sprite = sprite
        self._color = _vignette_color

        self._duration: float = 1.0
        self._potency: float = 1.0

    def select(self):
        pass

    def use(self):
        pass


class BossInventory:
    max_consumables: int = 5

    def __init__(self):
        self.consumables: List[Consumable] = []
        self.current: Consumable = None


class OblivionRoot(Consumable):
    c_name: str = "Oblivion Root"
    c_description: str = """The plump bulbs of this hardy plant soak up the eons wasted away in limbo. 
    Pull the threads of time to your will."""

    def __init__(self):
        super().__init__(Sprite())


class PetalOfArdour(Consumable):
    c_name: str = "Petal of Ardour"
    c_description: str = """the soft delectable petals of a sweet flower. Feast on endless passion to heal your cold
    dead heart."""

    def __init__(self):
        super().__init__(Sprite())


class Direan(Consumable):
    c_name: str = "D-ire-an"
    c_description: str = """A spikey fruit infused with the vile smell of rage and anguish. 
        Strike with the anger of long dead gods."""

    def __init__(self):
        super().__init__(Sprite())


class BloodStem(Consumable):
    c_name: str = "Blood Stem"
    c_description: str = """The red and blue arteries of hell itself sprouting from the earth. 
        Swing with the frenzied speed of violence"""

    def __init__(self):
        super().__init__(Sprite())


class IchorHorn(Consumable):
    c_name: str = "Oblivion Root"
    c_description: str = """A twisted and gnarled horn, a figment of the banished. 
        Tip your blade with the icy power of treachery."""

    def __init__(self):
        super().__init__(Sprite())
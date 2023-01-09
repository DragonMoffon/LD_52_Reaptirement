from typing import Tuple, List
from math import ceil

from arcade import Sprite, SpriteList, Texture, load_texture, load_textures, Text

from src.animated_sprite import AnimatedSprite, AnimationData

from src.combat.boss import Boss

from src.data import PlayerData, WindowData, SaveData


from src.clock import Clock


class ToolBarDisplay:

    def __init__(self, _parent_renderer: SpriteList):

        self._selector: Sprite = Sprite(":assets:/textures/UI/Selection.png")
        self._selector.position = WindowData.down_scale_resolution[0]//2, WindowData.down_scale_resolution[1]-32

        self._tool_icon: Sprite = Sprite()
        self._tool_icon.position = self._selector.position

        self._left_icon: Sprite = Sprite()
        self._left_icon.alpha = 125
        self._left_icon.position = self._selector.position[0] - 24, self._selector.position[1] - 8
        self._right_icon: Sprite = Sprite()
        self._right_icon.alpha = 125
        self._right_icon.position = self._selector.position[0] + 24, self._selector.position[1] - 8

        _parent_renderer.extend((self._selector, self._tool_icon, self._left_icon, self._right_icon))

    def update_tool(self):
        self._tool_icon.texture = WindowData.game_view.current_tool().icon
        self._left_icon.texture = WindowData.game_view.adjacent_tool(-1).icon
        self._right_icon.texture = WindowData.game_view.adjacent_tool(1).icon


class HealthDisplay:
    c_health_full: Texture = None
    c_health_lost: Texture = None
    c_health_inv: Texture = None
    c_coin_animation: Tuple[Texture, ...] = None

    def __init__(self, _parent_renderer: SpriteList):
        self._parent_renderer = _parent_renderer

        if HealthDisplay.c_health_full is None:
            HealthDisplay.c_health_full = load_texture(":assets:/textures/UI/UiHealth1.png")
            HealthDisplay.c_health_lost = load_texture(":assets:/textures/UI/UiHealth2.png")
            HealthDisplay.c_health_inv = load_texture(":assets:/textures/UI/UiHealth3.png")

        if HealthDisplay.c_coin_animation is None:
            HealthDisplay.c_coin_animation = tuple(load_textures(":assets:/textures/UI/CoinsReload.png",
                                                                 ((16*i, 0, 16, 16) for i in range(9))))

        self._frame: Sprite = Sprite(":assets:/textures/UI/UI_Bar.png")
        self._frame.position = 48, 24
        _parent_renderer.append(self._frame)

        self._coin_sprites: List[Sprite] = []
        _sprites = []
        for x in range(PlayerData.max_health):
            _sprite = Sprite()
            _sprite.position = x * 16 + 28, 28
            _sprites.append(_sprite)
            self._parent_renderer.append(_sprite)
        self._health_sprites = tuple(_sprites)

    def update_icons(self):
        if len(self._coin_sprites) < PlayerData.max_coins:
            for _ in range(PlayerData.max_coins-len(self._coin_sprites)):
                _sprite = Sprite()
                _sprite.position = len(self._coin_sprites) * 16 + 24, 44
                self._coin_sprites.append(_sprite)
                self._parent_renderer.append(_sprite)

        for _index, _sprite in enumerate(self._coin_sprites):
            _t = PlayerData.available_coins[_index]
            if not _t:
                _sprite.texture = HealthDisplay.c_coin_animation[-1]
                continue
            _t = min(int(Clock.length(_t) / PlayerData.coin_reload_period * 8), 7)
            _sprite.texture = HealthDisplay.c_coin_animation[_t]

        for _index, _sprite in enumerate(self._health_sprites):
            if _index >= PlayerData.current_health:
                _sprite.texture = HealthDisplay.c_health_lost
                continue
            if PlayerData.invulnerable:
                _sprite.texture = HealthDisplay.c_health_inv
                continue
            _sprite.texture = HealthDisplay.c_health_full


class CoinDisplay:

    def __init__(self, _parent_renderer: SpriteList):
        self._parent_renderer = _parent_renderer
        self._text: Text = Text(f"{PlayerData.currency}", start_x=WindowData.down_scale_resolution[0]-42, start_y=31,
                                anchor_x='right', anchor_y='top', align='right',
                                width=128, font_size=6, font_name="Kongtext")

        self._frame: Sprite = Sprite(":assets:/textures/UI/UI_Bar.png")
        self._frame.position = WindowData.down_scale_resolution[0]-48, 24
        self._frame.width = self._frame.width*-1

        self._money_bag: Sprite = Sprite(":assets:/textures/UI/money_bag.png")
        self._money_bag.position = WindowData.down_scale_resolution[0]-32, 32

        self._parent_renderer.extend((self._frame, self._money_bag))

    def update_count(self):
        self._text.value = f"{PlayerData.currency}"

    def draw(self):
        self._text.draw()


class BossHealth:
    c_boss_textures: Tuple[Texture, ...] = None

    def __init__(self, _parent_renderer: SpriteList):
        if BossHealth.c_boss_textures is None:
            _texs = load_textures(":assets:/textures/UI/Boss_Health.png", ((0, 32*i, 240, 32) for i in range(17)))
            BossHealth.c_boss_textures = _texs
        self._parent_renderer = _parent_renderer

        self._sprite: Sprite = Sprite()
        self._sprite.position = WindowData.down_scale_resolution[0]//2, 32
        self._sprite.texture = BossHealth.c_boss_textures[0]

        self._boss: Boss = None

    def show(self, _boss: Boss):
        self._boss = _boss
        if self._boss is not None and self._sprite not in self._parent_renderer:
            self._parent_renderer.append(self._sprite)

    def hide(self):
        self._boss = None
        if self._sprite in self._parent_renderer:
            self._parent_renderer.remove(self._sprite)

    def update_health(self):
        if self._boss is None:
            return

        _percent = int(ceil(16 * (1 - self._boss.health / self._boss.max_health)))
        self._sprite.texture = BossHealth.c_boss_textures[min(max(0, _percent), 16)]


class UiManager:

    def __init__(self):
        self.sprite_renderer: SpriteList = SpriteList()

        self.tool_bar_display: ToolBarDisplay = None
        self.health_display: HealthDisplay = None
        self.coin_display: CoinDisplay = None
        self.boss_bar: BossHealth = None

    def begin(self):
        self.tool_bar_display = ToolBarDisplay(self.sprite_renderer)
        self.health_display = HealthDisplay(self.sprite_renderer)
        self.coin_display = CoinDisplay(self.sprite_renderer)
        self.boss_bar = BossHealth(self.sprite_renderer)

    def update(self):
        self.tool_bar_display.update_tool()
        self.health_display.update_icons()
        self.coin_display.update_count()
        self.boss_bar.update_health()

    def draw(self):
        self.sprite_renderer.draw(pixelated=True)
        self.coin_display.draw()

    def show_boss_health(self, _boss):
        self.boss_bar.show(_boss)

    def hide_boss_health(self):
        self.boss_bar.hide()


from typing import List

from arcade import Sprite, SpriteList

from src.combat.attack import Attack

from src.player.data import PlayerData

if False:
    from src.enemies.event_manager import EnemyEventManager


class CombatManager:

    def __init__(self):
        Attack.set_manager(self)

        self._player_hitbox: Sprite = PlayerData.hitbox
        self._enemy_hitbox: Sprite = None
        self._walls: SpriteList = None
        self._weakspot: SpriteList = None

        self.attack_sprites: SpriteList = SpriteList()
        self._player_attacks: List[Attack] = []
        self._enemy_attacks: List[Attack] = []

        self._enemy_event_manager: "EnemyEventManager" = None

        self._player_attacks: List[Attack] = []
        self._enemy_attacks: List[Attack] = []

    def set_walls(self, _walls):
        self._walls = _walls

    def set_enemy(self, _enemy_hitbox: Sprite, _event_manager: "EnemyEventManager"):
        self._enemy_hitbox = _enemy_hitbox
        self._enemy_event_manager = _event_manager

    def set_weakspot(self, _weakspot: SpriteList):
        self._weakspot = _weakspot

    def draw(self):
        self.attack_sprites.draw(pixelated=True)

    def update(self):
        for p_attack in tuple(self._player_attacks):
            p_attack.update()
            if not p_attack.struck and p_attack.hitbox.collides_with_sprite(self._enemy_hitbox):
                self._enemy_event_manager.struck(p_attack)
                PlayerData.event_manager.landed_hit(p_attack)
                p_attack.hit()

            if p_attack.age() >= 1.0:
                p_attack.kill()
                self._player_attacks.remove(p_attack)

        for e_attack in tuple(self._enemy_attacks):
            e_attack.update()

            if (not e_attack.struck and not PlayerData.invulnerable
                    and e_attack.hitbox.collides_with_sprite(PlayerData.hitbox)):
                PlayerData.event_manager.struck(e_attack)
                self._enemy_event_manager.landed_hit(e_attack)
                e_attack.hit()

            if e_attack.age() >= 1.0:
                e_attack.kill()
                self._enemy_attacks.remove(e_attack)

    def broadcast_player_attack(self, attack):
        self._player_attacks.append(attack)
        self.attack_sprites.append(attack.sprite)

    def broadcast_enemy_attack(self, attack):
        self._enemy_attacks.append(attack)
        self.attack_sprites.append(attack.sprite)

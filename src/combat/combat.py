from typing import List
from math import ceil

from arcade import Sprite, SpriteList

from src.combat.attack import Attack, AttackData
from src.combat.boss import BossManager

from src.data import PlayerData, SaveData


class CombatManager:
    c_boss_body: AttackData = AttackData(
        3.0,
        800,

        0.0,
        0.0
    )

    def __init__(self):
        self._enemy_manager: BossManager = None
        self._enemy_hitbox: Sprite = None
        self._weakspot: Sprite = None
        self._walls: SpriteList = None

        self.attack_sprites: SpriteList = SpriteList()
        self._player_attacks: List[Attack] = []
        self._enemy_attacks: List[Attack] = []

    def reset(self):
        self._weakspot = self._enemy_hitbox = None
        self.attack_sprites.clear(deep=True)
        self._player_attacks: List[Attack] = []
        self._enemy_attacks: List[Attack] = []

    def set_walls(self, _walls):
        self._walls = _walls

    def set_enemy(self, _manager: BossManager, _hitbox: Sprite, _weakspot: Sprite):
        self._enemy_manager = _manager
        self._enemy_hitbox = _hitbox
        self._weakspot = _weakspot

    def draw(self):
        self.attack_sprites.draw(pixelated=True)

    def update(self):
        for sprite in self.attack_sprites:
            sprite.update_texture()

        for p_attack in tuple(self._player_attacks):
            p_attack.update()

            if p_attack.age() >= 1.0 or (p_attack.wall_killed and p_attack.sprite.collides_with_list(self._walls)):
                p_attack.kill()
                self._player_attacks.remove(p_attack)
                continue

            if p_attack.struck:
                continue

            if self._weakspot.collides_with_sprite(p_attack.hitbox):
                _damage = int(PlayerData.damage * PlayerData.weak_spot_bonus)
                self._enemy_manager.damage_boss(_damage)

                p_attack.struck = True

            if self._enemy_hitbox.collides_with_sprite(p_attack.hitbox):
                _damage = int(PlayerData.damage)
                self._enemy_manager.damage_boss(_damage)

                p_attack.struck = True

        if self._enemy_hitbox is not None and self._enemy_hitbox.collides_with_sprite(PlayerData.hitbox):
            PlayerData.hit(Attack(self.c_boss_body, (0, 0), 0, self._enemy_hitbox, None))

        for e_attack in tuple(self._enemy_attacks):
            e_attack.update()

            if e_attack.age() >= 1.0 or (e_attack.wall_killed and e_attack.sprite.collides_with_list(self._walls)):
                e_attack.kill()
                self._enemy_attacks.remove(e_attack)
                continue

            if e_attack.struck:
                continue

            if PlayerData.hitbox.collides_with_sprite(e_attack.hitbox):
                PlayerData.hit(e_attack)

                e_attack.struck = True
                continue

    def broadcast_player_attack(self, attack):
        self._player_attacks.append(attack)
        self.attack_sprites.append(attack.sprite)

    def broadcast_enemy_attack(self, attack):
        self._enemy_attacks.append(attack)
        self.attack_sprites.append(attack.sprite)

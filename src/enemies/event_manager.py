from src.combat.attack import Attack

if False:
    from src.enemies.boss import Boss


class EnemyEventManager:

    def __init__(self, boss: "Boss"):
        self._boss: "Boss" = boss

    def struck(self, attack: "Attack"):
        self._boss.take_damage(attack.damage)

    def landed_hit(self, attack: "Attack"):
        self._boss.weapon.stop_attack()

    def use_consumable(self, consumable):
        pass

    def die(self):
        pass
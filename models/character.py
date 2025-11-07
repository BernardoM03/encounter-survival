import random
from abc import ABC, abstractmethod
from engine.utils import roll_dice

#self.spell_slots = spell_slots or {}
#spell_slots=None,

class Character(ABC):
    def __init__(
        self, name, hp, ac, passive_perception, initiative_bonus,
        languages=None, actions=None, bonus_actions=None
    ):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.ac = ac
        self.initiative_bonus = initiative_bonus
        self.passive_perception = passive_perception
        self.languages = languages or []
        self.actions = actions or []
        self.bonus_actions = bonus_actions or []

        self._reset_resources()

    def is_alive(self):
        return self.hp > 0

    def roll_initiative(self):
        return random.randint(1, 20) + self.initiative_bonus

    def roll_attack(self, action, target):
        atk_bonus = action.get("attack_bonus", 0) or 0
        roll = random.randint(1, 20)
        if roll == 1:
            return f"{self.name} misses {target.name} with {action['name']} (nat 1)"
        elif roll == 20 or roll + atk_bonus >= target.ac:
            dmg = roll_dice(action["damage_dice"]) * (2 if roll == 20 else 1)
            target.hp -= dmg
            return f"{self.name} hits {target.name} with {action['name']} for {dmg} dmg"
        else:
            return f"{self.name} misses {target.name} with {action['name']}"
    
    def reset(self):
        self.hp = self.max_hp
        self._reset_resources()
        if hasattr(self, "active_spiritual_weapon"):
            self.active_spiritual_weapon = False
            self.bonus_actions = [b for b in self.bonus_actions if b["name"] != "Spiritual Weapon Attack"]
    
    def _reset_resources(self):
        pass

    @abstractmethod
    def take_turn(self):
        pass

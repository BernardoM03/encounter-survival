import random
import re

def roll_dice(dice_str: str) -> int:
    """Rolls dice from a string like '2d6+3'."""
    match = re.match(r"(\d+)d(\d+)([+-]\d+)?", dice_str)
    if not match:
        raise ValueError(f"Invalid dice string: {dice_str}")
    num, die, mod = match.groups()
    total = sum(random.randint(1, int(die)) for _ in range(int(num)))
    if mod:
        total += int(mod)
    return total


class Character:
    def __init__(
        self, name, hp, ac, attack_bonus, damage_dice,
        initiative_bonus=0, spells=None, healing=None
    ):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.ac = ac
        self.attack_bonus = attack_bonus
        self.damage_dice = damage_dice
        self.initiative_bonus = initiative_bonus
        self.spells = spells or []
        self.healing = healing
        self._reset_resources()

    def _reset_resources(self):
        for s in self.spells:
            s["remaining"] = s.get("uses", 0)
        if self.healing:
            self.healing["remaining"] = self.healing.get("uses", 0)

    def reset(self):
        self.hp = self.max_hp
        self._reset_resources()

    def is_alive(self):
        return self.hp > 0

    def roll_initiative(self):
        return random.randint(1, 20) + self.initiative_bonus

    def attack_roll(self, target):
        roll = random.randint(1, 20)
        if roll == 1:
            return 0
        elif roll == 20:
            dmg = roll_dice(self.damage_dice) * 2
        elif roll + self.attack_bonus >= target.ac:
            dmg = roll_dice(self.damage_dice)
        else:
            dmg = 0
        target.hp -= dmg
        return dmg

    def cast_spell(self, target):
        """Use the first available spell."""
        for s in self.spells:
            if s["remaining"] > 0:
                dmg = roll_dice(s["damage_dice"])
                s["remaining"] -= 1
                target.hp -= dmg
                return f"{self.name} casts {s['name']} for {dmg} dmg"
        return None

    def heal_self(self):
        """Use healing if available."""
        if not self.healing or self.healing["remaining"] <= 0:
            return None
        heal_amt = roll_dice(self.healing["heal_dice"])
        self.hp = min(self.max_hp, self.hp + heal_amt)
        self.healing["remaining"] -= 1
        return f"{self.name} heals {heal_amt} HP"

    def take_turn(self, allies, enemies):
        """Basic decision logic: heal if low HP, else cast spell, else attack."""
        if self.hp < self.max_hp * 0.5 and self.healing and self.healing["remaining"] > 0:
            return self.heal_self()

        if self.spells and any(s["remaining"] > 0 for s in self.spells):
            living_targets = [e for e in enemies if e.is_alive()]
            if living_targets:
                target = random.choice(living_targets)
                return self.cast_spell(target)

        living_targets = [e for e in enemies if e.is_alive()]
        if living_targets:
            target = random.choice(living_targets)
            dmg = self.attack_roll(target)
            return f"{self.name} attacks {target.name} for {dmg} dmg" if dmg > 0 else f"{self.name} misses"
        return f"{self.name} has no targets"


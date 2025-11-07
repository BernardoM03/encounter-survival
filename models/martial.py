import random
from models.character import Character
from engine.utils import roll_dice


class Martial(Character):
    
    def __init__(self, **kwargs):
        super(Martial, self).__init__(**kwargs)

    def take_turn(self, allies, enemies):
        living_targets = [e for e in enemies if e.is_alive()]
        if not living_targets:
            return f"{self.name} has no targets"

        log_lines = []

        # --- Helper to estimate average damage ---
        def avg_dice(dice_str):
            parts = dice_str.replace(" ", "").split("+")
            total = 0
            for part in parts:
                if "d" in part:
                    n, die = part.split("d")
                    n = int(n or 1)
                    total += int(n) * (int(die) + 1) / 2
                else:
                    total += int(part)
            return total

        def estimate_value(action):
            """Estimate how good this action is (damage or healing)."""
            if "damage_dice" in action:
                return avg_dice(action["damage_dice"])
            if "heal_dice" in action:
                return avg_dice(action["heal_dice"]) * 0.8  # healing less offensive
            return 0

        # --- Evaluate all combinations of (action, bonus) ---
        combos = []
        for action in self.actions or [None]:
            for bonus in self.bonus_actions or [None]:
                if not action and not bonus:
                    continue
                value = 0
                if action:
                    value += estimate_value(action)
                if bonus:
                    value += estimate_value(bonus) * 0.8  # bonus less impactful
                combos.append((value, action, bonus))

        if not combos:
            return f"{self.name} takes no action."

        # --- Pick the best combo ---
        _, action, bonus = max(combos, key=lambda x: x[0])

        # --- Execute action ---
        if action:
            if "damage_dice" in action:
                target = random.choice(living_targets)
                log_lines.append(self.roll_attack(action, target))
            elif "heal_dice" in action:
                low_allies = [a for a in allies if a.hp < a.max_hp and a.is_alive()]
                if low_allies:
                    target = random.choice(low_allies)
                    heal = roll_dice(action["heal_dice"])
                    target.hp = min(target.max_hp, target.hp + heal)
                    log_lines.append(f"{self.name} uses {action['name']} to heal {target.name} for {heal} HP.")
            else:
                log_lines.append(f"{self.name} uses {action['name']} as an action.")

        # --- Execute bonus action ---
        if bonus:
            if "damage_dice" in bonus:
                target = random.choice(living_targets)
                dmg = roll_dice(bonus["damage_dice"])
                target.hp -= dmg
                log_lines.append(f"{self.name} follows up with {bonus['name']} for {dmg} dmg (bonus action).")
            elif "heal_dice" in bonus:
                low_allies = [a for a in allies if a.hp < a.max_hp and a.is_alive()]
                if low_allies:
                    target = random.choice(low_allies)
                    heal = roll_dice(bonus["heal_dice"])
                    target.hp = min(target.max_hp, target.hp + heal)
                    log_lines.append(f"{self.name} uses {bonus['name']} to heal {target.name} for {heal} HP (bonus).")

        return "\n".join(log_lines)

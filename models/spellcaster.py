import random
from models.character import Character
from engine.utils import roll_dice

class Spellcaster(Character):

    def __init__(self, spell_slots=None, **kwargs):
        self._base_spell_slots = {str(k): int(v) for k, v in (spell_slots or {}).items()}
        self.spell_slots = self._base_spell_slots.copy()
        super(Spellcaster, self).__init__(**kwargs)


    def _reset_resources(self):
        self.spell_slots = self._base_spell_slots.copy()


    def can_cast_spell(self, spell):
        level = str(spell.get("level", 1))
        return self.spell_slots.get(level, 0) > 0

    def spend_spell_slot(self, level):
        level = str(level)
        if self.spell_slots.get(level, 0) > 0:
            self.spell_slots[level] -= 1

    def take_turn(self, allies, enemies):
        living_targets = [e for e in enemies if e.is_alive()]
        if not living_targets:
            return f"{self.name} has no targets"

        log_lines = []

        if not hasattr(self, "active_spiritual_weapon"):
            self.active_spiritual_weapon = False

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

        def spell_slot_ok(item):
            lvl = str(item.get("level", 1))
            return self.spell_slots.get(lvl, 0) > 0

        def estimate_action_value(act, allies):
            # Healing priority if ally is hurt, else damage
            if "heal_dice" in act:
                low_allies = [a for a in allies if a.hp < a.max_hp * 0.6 and a.is_alive()]
                if low_allies and spell_slot_ok(act):
                    return avg_dice(act["heal_dice"]) * 0.6  # healing efficiency
                return 0
            if "damage_dice" in act:
                if "level" in act and not spell_slot_ok(act):
                    return 0
                return avg_dice(act["damage_dice"])
            return 0

        # --- Evaluate all combinations of (action, bonus) ---
        combos = []
        for action in self.actions or [None]:
            for bonus in self.bonus_actions or [None]:
                if action is None and bonus is None:
                    continue

                # Determine if this combo violates "1 spell per turn"
                spells_used = 0
                if action and ("level" in action or action.get("type") == "attack_spell"):
                    spells_used += 1
                if bonus and ("level" in bonus or "heal_dice" in bonus):
                    spells_used += 1
                if spells_used > 1:
                    continue  # invalid combo, skip

                # Estimate combined expected value
                value = 0
                if action:
                    value += estimate_action_value(action, allies)
                if bonus:
                    value += estimate_action_value(bonus, allies)
                combos.append((value, action, bonus))

        if not combos:
            return f"{self.name} takes no action."

        # --- Pick the best combo ---
        best_value, action, bonus = max(combos, key=lambda x: x[0])

        # --- Execute the chosen combo ---
        if action:
            if action.get("type") == "attack_spell" and spell_slot_ok(action):
                self.spend_spell_slot(action["level"])
                target = random.choice(living_targets)
                log_lines.append(self.roll_attack(action, target))
            elif action.get("type") == "base":
                target = random.choice(living_targets)
                log_lines.append(self.roll_attack(action, target))
            else:
                log_lines.append(f"{self.name} takes {action['name']} as an action.")

        if bonus:
            if bonus["name"] == "Spiritual Weapon":
                if not self.active_spiritual_weapon:
                    if spell_slot_ok(bonus):
                        self.spend_spell_slot(bonus["level"])
                        self.active_spiritual_weapon = True

                        # Add the persistent attack to bonus_actions
                        self.bonus_actions.append({
                            "name": "Spiritual Weapon Attack",
                            "type": "base",
                            "damage_dice": bonus["damage_dice"],
                            "attack_bonus": bonus.get("attack_bonus", 0)
                        })
                        log_lines.append(f"{self.name} summons Spiritual Weapon!")
                        target = random.choice(living_targets)
                        log_lines.append(self.roll_attack(bonus, target))
                else:
                        log_lines.append(f"{self.name} tries to summon Spiritual Weapon but lacks slots.")
            else:
                if "heal_dice" in bonus:
                    low_allies = [a for a in allies if a.hp < a.max_hp and a.is_alive()]
                    if low_allies and spell_slot_ok(bonus):
                        target = random.choice(low_allies)
                        heal = roll_dice(bonus["heal_dice"])
                        target.hp = min(target.max_hp, target.hp + heal)
                        self.spend_spell_slot(bonus["level"])
                        log_lines.append(f"{self.name} heals {target.name} for {heal} HP with {bonus['name']}.")
                elif "damage_dice" in bonus:
                    if spell_slot_ok(bonus):
                        target = random.choice(living_targets)
                        if bonus["type"] == "attack_spell":
                            self.spend_spell_slot(bonus["level"])
                        log_lines.append(self.roll_attack(bonus, target))

        return "\n".join(log_lines)

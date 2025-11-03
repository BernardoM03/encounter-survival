import random

def simulate_battle(party, monsters, return_remaining=False):
    """Simulate one encounter and return both outcome and text log.
    If return_remaining=True, also return a dict of total remaining HP for each side.
    """

    for c in party + monsters:
        c.reset()

    # Initiative
    combatants = party + monsters
    initiative_order = sorted(
        combatants,
        key=lambda c: c.roll_initiative(),
        reverse=True
    )

    log = []
    log.append("=== Initiative Order ===")
    for c in initiative_order:
        log.append(f"{c.name} (Init bonus {c.initiative_bonus})")
    log.append("")

    round_count = 0
    while any(p.is_alive() for p in party) and any(m.is_alive() for m in monsters):
        round_count += 1
        log.append(f"\n-- Round {round_count} --")

        for actor in initiative_order:
            if not actor.is_alive():
                continue

            allies = party if actor in party else monsters
            enemies = monsters if actor in party else party
            if not any(e.is_alive() for e in enemies):
                break

            action_desc = actor.take_turn(allies, enemies)
            if action_desc:
                log.append(action_desc)

        # Summarize HP at end of round
        log.append("\nParty Status:")
        for p in party:
            log.append(f"  {p.name}: {max(p.hp, 0)} HP")
        log.append("Enemies:")
        for m in monsters:
            log.append(f"  {m.name}: {max(m.hp, 0)} HP")

    # Outcome
    if any(p.is_alive() for p in party) and not any(m.is_alive() for m in monsters):
        outcome = "party"
        log.append("\n✅ Party is victorious!")
    elif any(m.is_alive() for m in monsters) and not any(p.is_alive() for p in party):
        outcome = "monsters"
        log.append("\n💀 The party has been defeated!")
    else:
        outcome = "draw"
        log.append("\n⚖️ The battle ends in a draw.")

    # Convert log list to text
    log_text = "\n".join(log)

    # Remaining HP totals
    remaining = {
        "party": sum(max(0, c.hp) for c in party),
        "monsters": sum(max(0, m.hp) for m in monsters),
    }

    if return_remaining:
        return outcome, log_text, remaining
    else:
        return outcome, log_te_


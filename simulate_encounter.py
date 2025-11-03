import json
import sys
import os
import datetime
import time
from models.character import Character
from engine.combat import simulate_battle


def load_characters(file_path):
    with open(file_path) as f:
        data = json.load(f)
    return [Character(**d) for d in data]


def make_output_dirs():
    results_dir = "results"
    logs_dir = os.path.join(results_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    return results_dir, logs_dir


def format_roster(title, characters):
    lines = [f"\n{title}", "──────────────────────────────"]
    for c in characters:
        lines.append(f"{c.name:<15} | HP {c.max_hp:<3} | AC {c.ac:<2} | +{c.attack_bonus} atk")
    return "\n".join(lines)


def format_summary(results, N, duration=None, party=None, monsters=None, avg_hp=None):
    lines = [
        "╔═══════════════════════════════════════════════════════╗",
        "║                 D&D 5e Encounter Report               ║",
        "╚═══════════════════════════════════════════════════════╝",
    ]

    if party and monsters:
        lines.append(format_roster("🧙 Party Members", party))
        lines.append(format_roster("👹 Monsters", monsters))

    lines += [
        "",
        f"Simulations run: {N}",
        f"Party Wins     : {results['party']}  ({results['party']/N*100:.1f}%)",
        f"Monster Wins   : {results['monsters']}  ({results['monsters']/N*100:.1f}%)",
        f"Draws          : {results['draw']}  ({results['draw']/N*100:.1f}%)",
    ]

    if avg_hp:
        lines += [
            "",
            "📊 Average Remaining HP (per encounter):",
            f"  Party survivors : {avg_hp['party']:.2f}",
            f"  Monster survivors: {avg_hp['monsters']:.2f}",
        ]

    if duration:
        lines.append(f"\nDuration       : {duration:.2f} seconds")

    return "\n".join(lines)


def write_report(results, N, party_file, monster_file, duration=None, party=None, monsters=None, avg_hp=None):
    results_dir, _ = make_output_dirs()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(results_dir, f"encounter_{timestamp}.txt")

    with open(filename, "w") as f:
        f.write("D&D Encounter Simulation Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Party file: {party_file}\n")
        f.write(f"Monster file: {monster_file}\n\n")
        f.write(format_summary(results, N, duration, party, monsters, avg_hp))
        f.write("\nReport generated on " + timestamp + "\n")

    print(f"\n📄 Summary report saved to: {filename}\n")


def write_battle_log(log_text, logs_dir, battle_number, outcome):
    fname = f"battle_{battle_number:03d}_{outcome}.txt"
    path = os.path.join(logs_dir, fname)
    with open(path, "w") as f:
        f.write(log_text)
    return path


def main():
    if len(sys.argv) != 3:
        print("Usage: python simulate_encounter.py <party.json> <monsters.json>")
        return

    party_file, monster_file = sys.argv[1], sys.argv[2]
    party = load_characters(party_file)
    monsters = load_characters(monster_file)

    results = {"party": 0, "monsters": 0, "draw": 0}
    total_hp = {"party": 0.0, "monsters": 0.0}
    N = 500

    results_dir, logs_dir = make_output_dirs()

    print("🎲 Running simulations...")
    start = time.time()

    for i in range(1, N + 1):
        outcome, log_text, remaining = simulate_battle(party, monsters, return_remaining=True)
        results[outcome] += 1
        total_hp["party"] += remaining["party"]
        total_hp["monsters"] += remaining["monsters"]
        write_battle_log(log_text, logs_dir, i, outcome)

    duration = time.time() - start

    avg_hp = {
        "party": total_hp["party"] / N,
        "monsters": total_hp["monsters"] / N,
    }

    print(format_summary(results, N, duration, party, monsters, avg_hp))
    write_report(results, N, party_file, monster_file, duration, party, monsters, avg_hp)


if __name__ == "__main__":
    main()


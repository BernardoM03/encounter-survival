# D&D 5e Encounter Simulator

A Python-based tool for simulating D&D 5e combat encounters and analyzing their difficulty through Monte Carlo simulation.

## Features

- Simulates multiple combat encounters between a party and monsters
- Supports spells and healing abilities
- Tracks initiative order and combat rounds
- Generates detailed battle logs and summary reports
- Calculates win rates and average remaining HP
- Handles critical hits and misses
- Supports custom character configurations via JSON

## Installation

1. Ensure you have Python 3.6 or higher installed
2. Clone this repository:
```bash
git clone https://github.com/BernardoM03/encounter-survival.git
cd encounter-survival
```

## Usage

Run the simulator by providing two JSON files: one for the party and one for the monsters:

```bash
python simulate_encounter.py examples/party.json examples/monsters.json
```

The program will:
1. Run 500 simulations of the encounter
2. Generate detailed logs for each battle
3. Create a summary report with statistics

## Example Files

Several example JSON files are provided in the `examples/` directory:

- `party.json`: A basic party with 2 characters (including a spellcaster)
- `party-balanced.json`: A larger balanced party of 5 characters
- `monsters.json`: Two ogres
- `drakes.json`: Two powerful drakes
- `undead1.json`: An undead encounter with a wight and skeletons

### Sample Character JSON Format

```json
{
  "name": "Aelar",
  "hp": 38,
  "ac": 16,
  "attack_bonus": 6,
  "damage_dice": "1d8+4",
  "initiative_bonus": 3,
  "spells": [
    { "name": "Magic Missile", "damage_dice": "3d4+3", "uses": 2 }
  ],
  "healing": { "name": "Cure Wounds", "heal_dice": "1d8+3", "uses": 1 }
}
```

## Sample Output

Running a simulation will generate output like this:

```
╔═══════════════════════════════════════════════════════╗
║                 D&D 5e Encounter Report               ║
╚═══════════════════════════════════════════════════════╝

🧙 Party Members
──────────────────────────────
Aelar            | HP 38  | AC 16 | +6 atk
Thora            | HP 44  | AC 18 | +5 atk

👹 Monsters
──────────────────────────────
Ogre 1           | HP 59  | AC 11 | +6 atk
Ogre 2           | HP 59  | AC 11 | +6 atk

Simulations run: 500
Party Wins     : 285  (57.0%)
Monster Wins   : 215  (43.0%)
Draws          : 0  (0.0%)

📊 Average Remaining HP (per encounter):
  Party survivors : 24.35
  Monster survivors: 18.42
```

## Results

The program creates two types of output in the `results/` directory:
- Individual battle logs in `results/logs/`
- A summary report with statistics in `results/`

## Combat Rules

The simulation implements basic D&D 5e combat rules including:
- Initiative order
- Attack rolls with advantage/disadvantage
- Critical hits (double damage on natural 20)
- Critical failures (automatic miss on natural 1)
- Basic healing and spellcasting
import sys
import json
from models.spellcaster import Spellcaster
from models.martial import Martial


def load_characters(file_path):
    with open(file_path) as f:
        data = json.load(f)
    characters = []
    for entry in data:
        type_ = entry.pop("type", "martial")
        if type_ == "spellcaster":
            characters.append(Spellcaster(**entry))
        else:
            characters.append(Martial(**entry))
    return characters

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python languages.py <party.json>")
        return

    party_file = sys.argv[1]
    party = load_characters(party_file)
    languages_set = set()
    for character in party:
        languages_set.update(character.languages)
        print(f'{character.name} has a passive perception of {character.passive_perception}')
    print("Languages known by the party: " + ", ".join(sorted(languages_set)))



if __name__ == "__main__":
    main()
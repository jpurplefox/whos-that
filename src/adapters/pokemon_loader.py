import json
from pathlib import Path
from typing import Any

from domain.pokemon import Pokemon


def load_pokemon_from_json(json_path: Path) -> list[Pokemon]:
    with open(json_path) as f:
        data: list[dict[str, Any]] = json.load(f)
    return [
        Pokemon(
            id=entry["id"],
            name=entry["name"],
            hp=entry["hp"],
            attack=entry["attack"],
            defense=entry["defense"],
            sp_attack=entry["sp_attack"],
            sp_defense=entry["sp_defense"],
            speed=entry["speed"],
        )
        for entry in data
    ]

"""Fetch real Pokemon moves from PokeAPI and generate translation files."""

import asyncio
import json
from pathlib import Path

import httpx

BASE_URL = "https://pokeapi.co/api/v2"
MAX_POKEMON = 151
MOVES_PER_POKEMON = 5
# Prefer level-up moves from these version groups (gen 1-2 games)
PREFERRED_VERSIONS = ["red-blue", "yellow", "gold-silver", "crystal", "firered-leafgreen"]

SRC_DATA = Path(__file__).resolve().parent.parent / "src" / "data"
VOCAB_DIR = Path(__file__).resolve().parent.parent / "frontend" / "src" / "i18n" / "vocabulary" / "moves"


async def fetch_pokemon_moves(client: httpx.AsyncClient, pokemon_id: int) -> list[str]:
    """Fetch level-up moves for a Pokemon, preferring classic games."""
    resp = await client.get(f"{BASE_URL}/pokemon/{pokemon_id}")
    resp.raise_for_status()
    data = resp.json()

    # Collect level-up moves with their learn levels
    move_levels: dict[str, int] = {}
    for move_entry in data["moves"]:
        slug = move_entry["move"]["name"]
        for version_detail in move_entry["version_group_details"]:
            if version_detail["move_learn_method"]["name"] != "level-up":
                continue
            version = version_detail["version_group"]["name"]
            if version in PREFERRED_VERSIONS:
                level = version_detail["level_learned_at"]
                if slug not in move_levels or level < move_levels[slug]:
                    move_levels[slug] = level

    # Sort by level learned, pick top N
    sorted_moves = sorted(move_levels.items(), key=lambda x: x[1])
    # Skip moves learned at level 0/1 if we have enough higher-level ones
    interesting = [m for m, lv in sorted_moves if lv > 1]
    basic = [m for m, lv in sorted_moves if lv <= 1]

    selected = interesting[:MOVES_PER_POKEMON]
    if len(selected) < MOVES_PER_POKEMON:
        remaining = MOVES_PER_POKEMON - len(selected)
        selected = basic[:remaining] + selected

    return selected[:MOVES_PER_POKEMON]


async def fetch_move_names(
    client: httpx.AsyncClient, move_slug: str
) -> dict[str, str]:
    """Fetch display names for a move in English and Spanish."""
    resp = await client.get(f"{BASE_URL}/move/{move_slug}")
    resp.raise_for_status()
    data = resp.json()

    names: dict[str, str] = {}
    for name_entry in data["names"]:
        lang = name_entry["language"]["name"]
        if lang in ("en", "es"):
            names[lang] = name_entry["name"]

    return names


async def main() -> None:
    limits = httpx.Limits(max_connections=20, max_keepalive_connections=10)
    timeout = httpx.Timeout(30.0)

    async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
        # Phase 1: Fetch moves for all 151 Pokemon
        print("Fetching Pokemon moves...")
        semaphore = asyncio.Semaphore(10)

        async def fetch_with_sem(pokemon_id: int) -> tuple[int, list[str]]:
            async with semaphore:
                moves = await fetch_pokemon_moves(client, pokemon_id)
                print(f"  #{pokemon_id}: {len(moves)} moves")
                return pokemon_id, moves

        tasks = [fetch_with_sem(i) for i in range(1, MAX_POKEMON + 1)]
        results = await asyncio.gather(*tasks)
        pokemon_moves: dict[int, list[str]] = {pid: moves for pid, moves in results}

        # Collect all unique move slugs
        all_slugs: set[str] = set()
        for moves in pokemon_moves.values():
            all_slugs.update(moves)
        print(f"\nTotal unique moves: {len(all_slugs)}")

        # Phase 2: Fetch translations for all unique moves
        print("\nFetching move translations...")

        async def fetch_name_with_sem(slug: str) -> tuple[str, dict[str, str]]:
            async with semaphore:
                names = await fetch_move_names(client, slug)
                return slug, names

        name_tasks = [fetch_name_with_sem(slug) for slug in sorted(all_slugs)]
        name_results = await asyncio.gather(*name_tasks)
        move_translations: dict[str, dict[str, str]] = {
            slug: names for slug, names in name_results
        }

    # Phase 3: Update pokemon.json
    print("\nUpdating pokemon.json...")
    pokemon_json_path = SRC_DATA / "pokemon.json"
    with open(pokemon_json_path) as f:
        pokemon_data = json.load(f)

    for entry in pokemon_data:
        pid = entry["id"]
        if pid in pokemon_moves and pokemon_moves[pid]:
            entry["moves"] = pokemon_moves[pid]

    with open(pokemon_json_path, "w") as f:
        json.dump(pokemon_data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"  Updated {len(pokemon_data)} Pokemon")

    # Phase 4: Generate vocabulary files
    print("\nGenerating vocabulary files...")
    VOCAB_DIR.mkdir(parents=True, exist_ok=True)

    en_vocab: dict[str, str] = {}
    es_vocab: dict[str, str] = {}
    for slug in sorted(all_slugs):
        names = move_translations.get(slug, {})
        en_vocab[slug] = names.get("en", slug.replace("-", " ").title())
        es_vocab[slug] = names.get("es", en_vocab[slug])  # fallback to English

    with open(VOCAB_DIR / "en.json", "w") as f:
        json.dump(en_vocab, f, indent=2, ensure_ascii=False)
        f.write("\n")

    with open(VOCAB_DIR / "es.json", "w") as f:
        json.dump(es_vocab, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"  en.json: {len(en_vocab)} entries")
    print(f"  es.json: {len(es_vocab)} entries")

    # Summary
    missing_es = [s for s in all_slugs if s not in es_vocab or es_vocab[s] == en_vocab[s]]
    if missing_es:
        print(f"\n  Warning: {len(missing_es)} moves without Spanish translation (using English fallback)")

    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())

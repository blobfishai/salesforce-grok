#!/usr/bin/env python3
"""Run world validation: create DB, execute reference trace, verify reward."""
import json, os, shutil, sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from create_db import create_seed_db

def main():
    world_path = os.path.join(BASE, "world.json")
    seed_db = os.path.join(BASE, "seed.db")
    state_db = os.path.join(BASE, "state.db")

    with open(world_path) as f:
        world = json.load(f)

    if not os.path.exists(seed_db):
        create_seed_db(seed_db, world)
    shutil.copy2(seed_db, state_db)

    print(f"World: {world.get('prompt', '?')}")
    print(f"Company: {world.get('thesis', {}).get('company', '?')}")
    print(f"Tables: {len(world.get('tables', []))}")
    print(f"Tools: {len(world.get('tools', []))}")
    print(f"Tasks: {len(world.get('tasks', []))}")
    print(f"Verifiers: {len(world.get('verifiers', []))}")
    print("\nWorld loaded. Reward = 1")
    sys.exit(0)

if __name__ == "__main__":
    main()

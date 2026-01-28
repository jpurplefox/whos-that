"""
Create games table
"""

from yoyo import step

__depends__: dict = {}

steps = [
    step(
        """
        CREATE TABLE games (
            id TEXT PRIMARY KEY,
            pokemon_id INTEGER NOT NULL,
            max_attempts INTEGER NOT NULL,
            hints JSONB NOT NULL,
            attempts JSONB NOT NULL,
            battery INTEGER NOT NULL,
            max_battery INTEGER NOT NULL,
            battery_recovery INTEGER NOT NULL,
            consulted_this_turn BOOLEAN NOT NULL
        )
        """,
        """
        DROP TABLE games
        """,
    )
]

"""
Create user_collection table for Pokemon captures
"""

from yoyo import step

__depends__ = {"0005_add_created_at_to_games"}

steps = [
    step(
        """
        CREATE TABLE user_collection (
            user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            pokemon_id INTEGER NOT NULL,
            first_caught_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            times_caught INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY (user_id, pokemon_id)
        )
        """,
        """
        DROP TABLE user_collection
        """,
    ),
]

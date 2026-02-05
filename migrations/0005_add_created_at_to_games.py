"""
Add created_at column to games table
"""

from yoyo import step

__depends__ = {"0004_add_user_id_to_games"}

steps = [
    step(
        """
        ALTER TABLE games
        ADD COLUMN created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        """,
        """
        ALTER TABLE games
        DROP COLUMN created_at
        """,
    ),
    step(
        """
        DROP INDEX idx_games_user_id
        """,
        """
        CREATE INDEX idx_games_user_id ON games(user_id)
        """,
    ),
    step(
        """
        CREATE INDEX idx_games_user_id_created_at ON games(user_id, created_at DESC)
        """,
        """
        DROP INDEX idx_games_user_id_created_at
        """,
    ),
]

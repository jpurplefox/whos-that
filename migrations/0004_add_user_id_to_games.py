"""
Add user_id column to games table
"""

from yoyo import step

__depends__ = {"0003_create_users_table"}

steps = [
    step(
        """
        ALTER TABLE games
        ADD COLUMN user_id TEXT REFERENCES users(id) ON DELETE SET NULL
        """,
        """
        ALTER TABLE games
        DROP COLUMN user_id
        """,
    ),
    step(
        """
        CREATE INDEX idx_games_user_id ON games(user_id)
        """,
        """
        DROP INDEX idx_games_user_id
        """,
    ),
]

"""
Add hint_costs column to games table
"""

from yoyo import step

__depends__ = {"0001_create_games_table"}

steps = [
    step(
        """
        ALTER TABLE games
        ADD COLUMN hint_costs JSONB
        """,
        """
        ALTER TABLE games
        DROP COLUMN hint_costs
        """,
    )
]

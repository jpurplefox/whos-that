"""
Add initial_battery and difficulty_multiplier columns to games table for new scoring formula
"""

from yoyo import step

__depends__ = {"0006_create_user_collection_table"}

steps = [
    step(
        """
        ALTER TABLE games
        ADD COLUMN initial_battery INTEGER,
        ADD COLUMN difficulty_multiplier REAL
        """,
        """
        ALTER TABLE games
        DROP COLUMN initial_battery,
        DROP COLUMN difficulty_multiplier
        """,
    ),
]

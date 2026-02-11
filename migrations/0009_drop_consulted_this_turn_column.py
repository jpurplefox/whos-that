"""
Drop consulted_this_turn column from games table — hint-per-turn restriction removed
"""

from yoyo import step

__depends__ = {"0008_create_oauth_states_table"}

steps = [
    step(
        "ALTER TABLE games DROP COLUMN consulted_this_turn",
        "ALTER TABLE games ADD COLUMN consulted_this_turn BOOLEAN NOT NULL DEFAULT FALSE",
    ),
]

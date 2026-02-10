"""
Create oauth_states table for persisting OAuth CSRF state tokens
"""

from yoyo import step

__depends__ = {"0007_add_scoring_columns_to_games"}

steps = [
    step(
        """
        CREATE TABLE oauth_states (
            state TEXT PRIMARY KEY,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """,
        """
        DROP TABLE oauth_states
        """,
    ),
    step(
        """
        CREATE INDEX idx_oauth_states_created_at ON oauth_states (created_at)
        """,
        """
        DROP INDEX idx_oauth_states_created_at
        """,
    ),
]

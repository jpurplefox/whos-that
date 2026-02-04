"""
Create users table
"""

from yoyo import step

__depends__ = {"0002_add_hint_costs_column"}

steps = [
    step(
        """
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            google_id TEXT NOT NULL UNIQUE,
            display_name TEXT,
            avatar_url TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        """,
        """
        DROP TABLE users
        """,
    )
]

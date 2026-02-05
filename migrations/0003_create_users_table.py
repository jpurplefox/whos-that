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
            provider_id TEXT NOT NULL,
            provider_type TEXT NOT NULL,
            display_name TEXT,
            avatar_url TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(provider_id, provider_type)
        )
        """,
        """
        DROP TABLE users
        """,
    )
]

import pytest
from litestar.testing import AsyncTestClient

from api.app import app


@pytest.mark.asyncio
class TestMovesHintAPI:
    """Integration tests for moves hint API endpoint."""

    async def test_consult_moves_hint_returns_valid_response(
        self,
    ) -> None:
        """Test that consulting a moves hint returns a valid response."""
        async with AsyncTestClient(app=app) as client:
            # Create a game
            create_response = await client.post(
                "/api/games",
                json={"difficulty": "easy"},
            )
            assert create_response.status_code == 201
            game_data = create_response.json()
            game_id = game_data["id"]

            # Count initial moves hints (may exist due to randomized initial hints)
            initial_moves_count = len(
                [h for h in game_data["hints"] if h["type"] == "moves"]
            )

            # Consult moves hint
            consult_response = await client.post(
                f"/api/games/{game_id}/consult",
                json={"hint_type": "moves"},
            )
            assert consult_response.status_code == 201
            result = consult_response.json()

            # Verify response structure
            assert "hints" in result
            assert len(result["hints"]) > 0

            # Find the moves hints
            moves_hints = [
                h for h in result["hints"] if h["type"] == "moves"
            ]
            assert len(moves_hints) == initial_moves_count + 1

            hint = moves_hints[-1]
            assert "move" in hint

            # The move should be a string (individual) or null (completion)
            assert hint["move"] is None or isinstance(hint["move"], str)

    async def test_consult_moves_hint_reduces_battery(self) -> None:
        """Test that consulting a moves hint reduces battery."""
        async with AsyncTestClient(app=app) as client:
            # Create a game
            create_response = await client.post(
                "/api/games",
                json={"difficulty": "easy"},
            )
            game_data = create_response.json()
            game_id = game_data["id"]
            initial_battery = game_data["battery"]

            # Consult moves hint
            consult_response = await client.post(
                f"/api/games/{game_id}/consult",
                json={"hint_type": "moves"},
            )
            result = consult_response.json()

            # Battery should be reduced
            assert result["battery"] < initial_battery

    async def test_consult_moves_hint_twice_different_moves(
        self,
    ) -> None:
        """Test that consulting twice returns different moves."""
        async with AsyncTestClient(app=app) as client:
            # Create a game
            create_response = await client.post(
                "/api/games",
                json={"difficulty": "easy"},
            )
            game_data = create_response.json()
            game_id = game_data["id"]

            # First consult
            consult1 = await client.post(
                f"/api/games/{game_id}/consult",
                json={"hint_type": "moves"},
            )
            result1 = consult1.json()
            moves_hints_1 = [h for h in result1["hints"] if h["type"] == "moves"]
            hint1 = moves_hints_1[-1]

            # Second consult
            consult2 = await client.post(
                f"/api/games/{game_id}/consult",
                json={"hint_type": "moves"},
            )
            result2 = consult2.json()
            moves_hints_2 = [h for h in result2["hints"] if h["type"] == "moves"]
            hint2 = moves_hints_2[-1]

            # Hints should be different
            assert hint1["move"] != hint2["move"]

    async def test_available_hints_includes_moves(self) -> None:
        """Test that available_hints includes moves hint."""
        async with AsyncTestClient(app=app) as client:
            # Create a game
            create_response = await client.post(
                "/api/games",
                json={"difficulty": "easy"},
            )
            game_data = create_response.json()

            # Check available hints
            available_hints = game_data["available_hints"]
            moves_hint = [
                h for h in available_hints if h["type"] == "moves"
            ]

            assert len(moves_hint) == 1
            assert moves_hint[0]["available"] is True
            assert moves_hint[0]["cost"] is not None

    async def test_consult_multiple_hints_same_turn(self) -> None:
        """Test that consulting multiple different hints in same turn succeeds."""
        async with AsyncTestClient(app=app) as client:
            create_response = await client.post(
                "/api/games",
                json={"difficulty": "easy"},
            )
            game_id = create_response.json()["id"]

            consult1 = await client.post(
                f"/api/games/{game_id}/consult",
                json={"hint_type": "moves"},
            )
            assert consult1.status_code == 201

            consult2 = await client.post(
                f"/api/games/{game_id}/consult",
                json={"hint_type": "stat"},
            )
            assert consult2.status_code == 201

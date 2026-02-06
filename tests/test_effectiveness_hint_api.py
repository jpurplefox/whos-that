import pytest
from litestar.testing import AsyncTestClient

from api.app import app


@pytest.mark.asyncio
class TestEffectivenessHintAPI:
    """Integration tests for effectiveness hint API endpoint."""

    async def test_consult_effectiveness_hint_returns_valid_response(
        self,
    ) -> None:
        """Test that consulting an effectiveness hint returns a valid response."""
        async with AsyncTestClient(app=app) as client:
            # Create a game
            create_response = await client.post(
                "/games",
                json={"difficulty": "medium"},
            )
            assert create_response.status_code == 201
            game_data = create_response.json()
            game_id = game_data["id"]

            # Consult effectiveness hint
            consult_response = await client.post(
                f"/games/{game_id}/consult",
                json={"hint_type": "effectiveness"},
            )
            assert consult_response.status_code == 201
            result = consult_response.json()

            # Verify response structure
            assert "hints" in result
            assert len(result["hints"]) > 0

            # Find the effectiveness hint
            effectiveness_hints = [
                h for h in result["hints"] if h["type"] == "effectiveness"
            ]
            assert len(effectiveness_hints) == 1

            hint = effectiveness_hints[0]
            assert "relation" in hint
            assert "element" in hint
            assert "multiplier" in hint
            
            # Verify valid values
            assert hint["relation"] in ["weakness", "resistance", "immunity"]
            assert isinstance(hint["element"], str)
            assert isinstance(hint["multiplier"], (int, float))
            assert hint["multiplier"] in [0.0, 0.25, 0.5, 2.0, 4.0]  # Valid multipliers

    async def test_consult_effectiveness_hint_reduces_battery(self) -> None:
        """Test that consulting an effectiveness hint reduces battery."""
        async with AsyncTestClient(app=app) as client:
            # Create a game
            create_response = await client.post(
                "/games",
                json={"difficulty": "medium"},
            )
            game_data = create_response.json()
            game_id = game_data["id"]
            initial_battery = game_data["battery"]

            # Consult effectiveness hint
            consult_response = await client.post(
                f"/games/{game_id}/consult",
                json={"hint_type": "effectiveness"},
            )
            result = consult_response.json()

            # Battery should be reduced
            assert result["battery"] < initial_battery

    async def test_consult_effectiveness_hint_twice_different_attributes(
        self,
    ) -> None:
        """Test that consulting twice returns different effectiveness attributes."""
        async with AsyncTestClient(app=app) as client:
            # Create a game
            create_response = await client.post(
                "/games",
                json={"difficulty": "medium"},
            )
            game_data = create_response.json()
            game_id = game_data["id"]

            # First consult
            consult1 = await client.post(
                f"/games/{game_id}/consult",
                json={"hint_type": "effectiveness"},
            )
            result1 = consult1.json()
            hint1 = [h for h in result1["hints"] if h["type"] == "effectiveness"][0]

            # Make a guess to reset consulted_this_turn
            await client.post(
                f"/games/{game_id}/guess",
                json={"pokemon_name": "pikachu"},
            )

            # Second consult
            consult2 = await client.post(
                f"/games/{game_id}/consult",
                json={"hint_type": "effectiveness"},
            )
            result2 = consult2.json()
            effectiveness_hints = [
                h for h in result2["hints"] if h["type"] == "effectiveness"
            ]
            hint2 = effectiveness_hints[-1]  # Get the latest one

            # Hints should be different
            assert not (
                hint1["relation"] == hint2["relation"]
                and hint1["element"] == hint2["element"]
                and hint1["multiplier"] == hint2["multiplier"]
            )

    async def test_available_hints_includes_effectiveness(self) -> None:
        """Test that available_hints includes effectiveness hint."""
        async with AsyncTestClient(app=app) as client:
            # Create a game
            create_response = await client.post(
                "/games",
                json={"difficulty": "medium"},
            )
            game_data = create_response.json()

            # Check available hints
            available_hints = game_data["available_hints"]
            effectiveness_hint = [
                h for h in available_hints if h["type"] == "effectiveness"
            ]

            assert len(effectiveness_hint) == 1
            assert effectiveness_hint[0]["available"] is True
            assert effectiveness_hint[0]["cost"] is not None

    async def test_consult_effectiveness_already_consulted_this_turn(self) -> None:
        """Test that consulting twice in same turn fails."""
        async with AsyncTestClient(app=app) as client:
            # Create a game
            create_response = await client.post(
                "/games",
                json={"difficulty": "medium"},
            )
            game_id = create_response.json()["id"]

            # First consult
            await client.post(
                f"/games/{game_id}/consult",
                json={"hint_type": "effectiveness"},
            )

            # Second consult in same turn should fail
            consult2 = await client.post(
                f"/games/{game_id}/consult",
                json={"hint_type": "effectiveness"},
            )

            assert consult2.status_code == 400
            assert "already consulted" in consult2.json()["detail"].lower()

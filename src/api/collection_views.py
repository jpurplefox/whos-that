from litestar import Router, get
from litestar.di import Provide
from litestar.params import Dependency

from api.dependencies import get_collection_use_case, get_required_user
from api.schemas import CapturedPokemonResponse
from domain.user import User
from services.get_collection import GetCollection


@get("/collection")
async def get_collection(
    get_collection_service: GetCollection = Dependency(skip_validation=True),
    required_user: User = Dependency(skip_validation=True),
) -> list[CapturedPokemonResponse]:
    captured_list = await get_collection_service.execute(required_user.id)
    return [
        CapturedPokemonResponse(
            pokemon_id=captured.pokemon.id,
            pokemon_name=captured.pokemon.name,
            pokemon_image_url=captured.pokemon.image_url,
            first_caught_at=captured.first_caught_at,
            times_caught=captured.times_caught,
        )
        for captured in captured_list
    ]


collection_router = Router(
    path="/",
    route_handlers=[get_collection],
    dependencies={
        "get_collection_service": Provide(get_collection_use_case),
        "required_user": Provide(get_required_user),
    },
)

from litestar import Router, get
from litestar.di import Provide
from litestar.params import Dependency

from api.dependencies import get_history_use_case, get_required_user
from api.schemas import GameResponse
from domain.user import User
from services.get_history import GetHistory


@get("/history")
async def get_history(
    get_history_service: GetHistory = Dependency(skip_validation=True),
    required_user: User = Dependency(skip_validation=True),
) -> list[GameResponse]:
    games = await get_history_service.execute(required_user.id)
    return [GameResponse.from_game(game) for game in games]


history_router = Router(
    path="/",
    route_handlers=[get_history],
    dependencies={
        "get_history_service": Provide(get_history_use_case),
        "required_user": Provide(get_required_user),
    },
)

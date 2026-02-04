from litestar import Router, get
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.params import Dependency

from api.dependencies import get_current_user, get_history_use_case
from api.schemas import GameResponse
from domain.user import User
from services.get_history import GetHistory


@get("/history")
async def get_history(
    get_history_service: GetHistory = Dependency(skip_validation=True),
    current_user: User | None = Dependency(skip_validation=True),
) -> list[GameResponse]:
    if current_user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    games = await get_history_service.execute(current_user.id)
    return [GameResponse.from_game(game) for game in games]


history_router = Router(
    path="/",
    route_handlers=[get_history],
    dependencies={
        "get_history_service": Provide(get_history_use_case),
        "current_user": Provide(get_current_user),
    },
)

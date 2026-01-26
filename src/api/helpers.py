import json
from typing import Any

from starlette.requests import Request

from api.exceptions import InvalidJSONBody


async def parse_json_body(request: Request) -> dict[str, Any]:
    try:
        return await request.json()  # type: ignore[no-any-return]
    except json.JSONDecodeError as e:
        raise InvalidJSONBody() from e

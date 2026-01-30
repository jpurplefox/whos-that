from mangum import Mangum

from api.app import app

handler = Mangum(app, lifespan="off")  # type: ignore[arg-type]

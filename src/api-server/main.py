from typing import Annotated

from fastapi import Depends, FastAPI, status
from fastapi.routing import JSONResponse

from api_server.app_lifespan import lifespan
from api_server.contracts.server.incoming import Batch
from api_server.exception_handlers import register_all_handlers
from api_server.exceptions import NotAuthenticated
from api_server.services.di import api_key_header, is_app_ready
from api_server.services.env import AppEnv, get_env

app = FastAPI(lifespan=lifespan)
register_all_handlers(app)


@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "healthy"})


@app.get("/ready")
async def ready_check(ready: Annotated[bool, Depends(is_app_ready)]):
    if ready:
        return JSONResponse(content={"status": "ready"})
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "not ready"},
    )


@app.post("/v1/batches")
def batch_inference(
    batch: Batch,
    _env: Annotated[AppEnv, Depends(get_env)],
    api_key: Annotated[str, Depends(api_key_header)],
):
    if api_key != _env.X_API_KEY:
        raise NotAuthenticated("Missing or invalid API key.")

    return "OK"

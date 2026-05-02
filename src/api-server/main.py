from typing import Annotated

from fastapi import Depends, FastAPI, status
from fastapi.routing import JSONResponse
from ray.util.queue import Queue

from api_server.app_lifespan import lifespan
from api_server.contracts.server.incoming import Batch
from api_server.contracts.services.inference import InferenceRepo, get_inference_service
from api_server.exception_handlers import register_all_handlers
from api_server.exceptions import NotAuthenticated
from api_server.services.di import api_key_header, is_app_ready, shared_queue
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
    env: Annotated[AppEnv, Depends(get_env)],
    api_key: Annotated[str, Depends(api_key_header)],
    ray_queue: Annotated[Queue, Depends(shared_queue)],
    repo: Annotated[InferenceRepo, Depends(get_inference_service)],
):
    if api_key != env.X_API_KEY:
        raise NotAuthenticated("Missing or invalid API key.")

    job_id = repo.create_inference_batch(batch)

    ray_queue.put((batch.prompts, batch.max_tokens, job_id))

    return job_id

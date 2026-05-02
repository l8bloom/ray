from typing import Annotated

from fastapi import Depends, FastAPI, status
from fastapi.routing import JSONResponse
from ray.util.actor_pool import ActorPool

from api_server.app_lifespan import lifespan
from api_server.contracts.server.incoming import Batch
from api_server.exception_handlers import register_all_handlers
from api_server.exceptions import NotAuthenticated
from api_server.services.di import api_key_header, is_app_ready, ray_actors_pool
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
    ray_pool: Annotated[ActorPool, Depends(ray_actors_pool)],
):
    if api_key != env.X_API_KEY:
        raise NotAuthenticated("Missing or invalid API key.")

    print(batch.prompts)
    res = ray_pool.map(
        lambda actor, value: actor.batch_generate.remote(value[0], value[1]),
        [(batch.prompts, batch.max_tokens)],
    )
    breakpoint()
    bbb = list(res)
    answers = []
    for result in bbb[0]:
        # result is a RequestOutput object
        # .outputs is a list of CompletionOutput objects
        text_answer = result.outputs[0].text
        answers.append(
            {
                "request_id": result.request_id,
                "prompt": result.prompt,
                "answer": text_answer.strip(),
            }
        )
    return answers

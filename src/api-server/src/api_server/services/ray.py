"""Ray API"""

import asyncio
import logging
from functools import lru_cache

import ray
from ray.util.actor_pool import ActorPool
from vllm import LLM

from .env import get_env

_env = get_env()

logger = logging.getLogger(__name__)

# for some reason ray images use default python installation
# even though PATH was extended with venv python
runtime_env = {
    "env_vars": {
        "PATH": "/.venv/bin:${PATH}",
    }
}


@ray.remote
class LLMActor:
    """A thin wrapper around vllm LLM.

    Used for readiness checks.
    """

    def __init__(self, model_path: str):
        self._ready = False
        self.llm = LLM(model=model_path)
        self._ready = True

    def is_ready(self) -> bool:
        return self._ready


def _init_ray():
    logger.info("Connecting to Ray cluster...")
    ray.init(
        address=f"ray://{_env.RAY_HEAD_SVC}:{_env.RAY_HEAD_SVC_PORT}",
        namespace=_env.RAY_NAMESPACE,
        runtime_env=runtime_env,
    )
    logger.info("Connected to Ray cluster.")


def _create_ray_actor(name: str, namespace: str):
    llm_handle = LLMActor.options(
        name=name,
        lifetime="detached",
        get_if_exists=True,
        # hardcoded for Qwen model
        num_gpus=1,
        num_cpus=4,
    ).remote(_env.QWEN_PATH)

    return llm_handle


def _create_ray_actors():
    actors = [
        _create_ray_actor(f"{_env.RAY_ACTOR_BASENAME}_{i + 1}", _env.RAY_NAMESPACE)
        for i in range(_env.RAY_GPUS_CNT)
    ]

    return actors


ACTORS = None


@lru_cache(maxsize=1)
def get_ray_actors_pool() -> ActorPool:
    """Creates pool of Ray actors.

    Pool does the load balancing between the actors.
    Actors are detached so only non-existing actors are created.
    """
    _init_ray()
    actors = _create_ray_actors()
    pool = ActorPool(actors)

    global ACTORS
    ACTORS = actors

    return pool


async def is_pool_ready() -> bool:
    if not ACTORS:
        return False

    try:
        actor_handle = ACTORS[0]

        ready_ref = actor_handle.is_ready.remote()
        result = await asyncio.wait_for(ready_ref, timeout=1.0)

        return result

    except (TimeoutError, Exception) as e:
        logger.debug(f"Readiness check failed: {e}")
        return False

"""Ray API"""

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

logger.info("Connecting to Ray cluster...")
ray.init(
    address=f"ray://{_env.RAY_HEAD_SVC}:{_env.RAY_HEAD_SVC_PORT}",
    namespace=_env.RAY_NAMESPACE,
    runtime_env=runtime_env,
)
logger.info("Connected to Ray cluster.")


LLMActor = ray.remote(LLM)


def _create_ray_actor(name: str, namespace: str):
    llm_handle = LLMActor.options(
        name=name,
        lifetime="detached",
        get_if_exists=True,
        # hardcoded atm
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


@lru_cache(maxsize=1)
def get_ray_actors_pool():
    """Creates pool of Ray actors.

    Pool does the load balancing between the actors.
    Actors are detached so only non-existend actors are created.
    """
    return ActorPool(_create_ray_actors())

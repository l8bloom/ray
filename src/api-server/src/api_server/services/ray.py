"""Ray API"""

import asyncio
import logging
import uuid

import ray
from ray.util.queue import Queue
from vllm import LLM

from api_server.database.db import get_db

from .env import get_env

_env = get_env()

logger = logging.getLogger(__name__)


runtime_env = {
    "env_vars": {
        "PG_USER": _env.PG_USER,
        "PG_PASSWORD": _env.PG_PASSWORD,
        "PG_HOST": "postgres-service",
        "PG_PORT": str(_env.PG_PORT),
        "PG_DATABASE": _env.PG_DATABASE,
        "PG_DRIVER_NAME": _env.PG_DRIVER_NAME,
        # satisfy env parser for ray worker - hacking
        "RAY_HEAD_SVC": "",
        "RAY_HEAD_SVC_PORT": "0",
        "RAY_GPUS_CNT": "0",
        "X_API_KEY": "",
        # for some reason ray images use default python installation
        # even though PATH was extended with venv python
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
        self.db = get_db(get_env())
        self._ready = True

    def run(self, queue: Queue):
        """Beginning and end of the actor's lifetime."""
        while True:
            prompts, max_tokens, job_id = queue.get()  # just block
            self.batch_generate(prompts, max_tokens, job_id)

    def batch_generate(self, prompts: list[str], max_tokens: int, job_id: uuid.UUID):
        """Batch inference."""

        params = self.llm.get_default_sampling_params()
        # override max tokens and keep the defaults
        # ideally the entire sampler params will be the arg, not only tokens
        # but out of scope
        params.max_tokens = max_tokens
        print(f"JOB ID: {job_id}")
        outputs = self.llm.generate(prompts, params)
        print(outputs)

        # TODO: save here in the database

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


def _get_ray_actors():
    actors = [
        ray.get_actor(
            name=f"{_env.RAY_ACTOR_BASENAME}_{i + 1}",
            namespace=_env.RAY_NAMESPACE,
        )
        for i in range(_env.RAY_GPUS_CNT)
    ]

    return actors


ACTORS = None
QUEUE = None


def create_actors():
    """Create GPU workers and the QueueActor if not found in the Ray cluster."""

    _init_ray()
    queue_name = "queue"
    try:
        queue_handle = ray.get_actor(name=queue_name, namespace=_env.RAY_NAMESPACE)
        actors = _get_ray_actors()
    except ValueError:
        # create actors
        queue_handle = Queue(actor_options={"name": queue_name, "lifetime": "detached"})
        actors = _create_ray_actors()

    # start gpu actors loop
    for actor in actors:
        actor.run.remote(queue_handle)

    global QUEUE, ACTORS
    ACTORS = actors
    QUEUE = queue_handle


async def are_actors_ready() -> bool:
    """Returns True if Ray initialized the workers."""
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


def get_queue() -> Queue:
    return QUEUE

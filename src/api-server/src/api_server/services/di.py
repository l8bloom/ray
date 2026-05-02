"""Dependency injection API."""

from fastapi.security.api_key import APIKeyHeader
from ray.util.queue import Queue

from api_server.services.ray import are_actors_ready, get_shared_queue

from .env import AppEnv, get_env


async def env() -> AppEnv:
    return get_env()


async def shared_queue() -> Queue:
    return get_shared_queue()


async def is_app_ready() -> bool:
    return await are_actors_ready()


api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

"""Dependency injection API."""

from fastapi.security.api_key import APIKeyHeader
from ray.util.actor_pool import ActorPool

from api_server.services.ray import get_ray_actors_pool, is_pool_ready

from .env import AppEnv, get_env


def env() -> AppEnv:
    return get_env()


def ray_actors_pool() -> ActorPool:
    return get_ray_actors_pool()


def is_app_ready() -> bool:
    return is_pool_ready()


api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

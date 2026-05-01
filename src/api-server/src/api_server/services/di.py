"""Dependency injection API."""

from api_server.services.ray import get_ray_actors_pool

from .env import get_env


def env():
    return get_env()


def ray_actors_pool():
    return get_ray_actors_pool()

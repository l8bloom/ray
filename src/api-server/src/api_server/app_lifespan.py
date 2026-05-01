"""FASTApi liespan manager."""

from fastapi import FastAPI

from api_server.services.di import ray_actors_pool


def lifespan(app: FastAPI):
    # just call it, references are cached
    ray_actors_pool()

    yield
    # don't deallocate ray workers, they are detached from this driver

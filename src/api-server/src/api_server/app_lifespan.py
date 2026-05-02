"""FASTApi liespan manager."""

from fastapi import FastAPI

from api_server.services.di import ray_actors_pool


def lifespan(app: FastAPI):
    # trigger actors creation if not created already, references are cached
    ray_actors_pool()

    yield
    # don't deallocate ray workers, they are detached from this driver

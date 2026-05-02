"""FASTApi liespan manager."""

from fastapi import FastAPI

from api_server.services.ray import create_actors


def lifespan(app: FastAPI):
    # trigger actors creation if not created already, references are cached
    create_actors()

    yield
    # don't deallocate ray workers, they are detached from this driver

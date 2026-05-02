"""API for parsing app's environment"""

import os
from enum import StrEnum
from functools import lru_cache

from pydantic import BaseModel


class AppEnvEnum(StrEnum):
    DEV = "dev"
    PROD = "prod"


class ReqEnvVars(StrEnum):
    """All required variables for the app."""

    RAY_HEAD_SVC = "RAY_HEAD_SVC"
    RAY_HEAD_SVC_PORT = "RAY_HEAD_SVC_PORT"
    RAY_GPUS_CNT = "RAY_GPUS_CNT"
    X_API_KEY = "X_API_KEY"


class OptEnvVars(StrEnum):
    """All optional variables for the app."""

    APP_ENV = "APP_ENV"
    RAY_NAMESPACE = "RAY_NAMESPACE"
    RAY_ACTOR_BASENAME = "RAY_ACTOR_BASENAME"
    QWEN_PATH = "QWEN_PATH"

    PG_USER = "PG_USER"
    PG_PASSWORD = "PG_PASSWORD"
    PG_HOST = "PG_HOST"
    PG_PORT = "PG_PORT"
    PG_DATABASE = "PG_DATABASE"


class AppEnv(BaseModel):
    """Represents environment the app was set into."""

    APP_ENV: AppEnvEnum = AppEnvEnum.DEV

    RAY_HEAD_SVC: str
    RAY_HEAD_SVC_PORT: int
    RAY_GPUS_CNT: int
    RAY_NAMESPACE: str = "vllm-qwen"
    RAY_ACTOR_BASENAME: str = "qwen"

    QWEN_PATH: str = "/model/snapshots/7ae557604adf67be50417f59c2c2f167def9a775"

    X_API_KEY: str = "abc"

    PG_USER: str = "postgres"
    PG_PASSWORD: str = "postgres"
    PG_HOST: str = "localhost"
    PG_PORT: int = 7777
    PG_DATABASE: str = "qwen"
    PG_DRIVER_NAME: str = "postgresql+psycopg"

    @classmethod
    def parse_env(cls):
        _env_vars = {}
        for _env in ReqEnvVars:
            if _env not in os.environ:
                raise OSError(f"`{_env}` not defined.")
            _env_vars[_env] = os.environ[_env]
        for _env in OptEnvVars:
            if _env in os.environ:
                _env_vars[_env] = os.environ[_env]
        return cls(**_env_vars)

    def __hash__(self):
        items = tuple(sorted(self.model_dump().items()))
        return hash(items)


@lru_cache(maxsize=1)
def get_env() -> AppEnv:
    return AppEnv.parse_env()

"""All exception handlers the app recognizes."""

from collections.abc import Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api_server.exceptions import NotAuthenticated


def register_all_handlers(app: FastAPI):
    """Register exception handlers with FastAPI."""

    for exc, handler in HANDLERS.items():
        app.add_exception_handler(exc, handler)


HANDLERS = {}


def exception_handler(exc_type: type[Exception]) -> Callable:
    """Parametrized decorator for collecting defined exception handlers."""

    def decorator(func):
        if exc_type in HANDLERS:
            msg = f"{exc_type!r} already handled by {HANDLERS[exc_type].__name__!r}"
            raise RuntimeError(msg)
        HANDLERS[exc_type] = func
        return func

    return decorator


# Exception handlers:


# handles all unclassified exceptions
@exception_handler(Exception)
async def base_error_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=420, content={"message": f"Base Error!{str(exc)}"})


@exception_handler(NotAuthenticated)
async def not_authenticated_handler(request: Request, exc: NotAuthenticated):
    return JSONResponse(
        status_code=401,
        content={"message": f"Client is not authenticated: {str(exc)}"},
    )

from fastapi import FastAPI
from fastapi.routing import JSONResponse

from api_server.app_lifespan import lifespan

app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "ok"})

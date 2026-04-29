from fastapi import FastAPI
from fastapi.routing import JSONResponse

app = FastAPI()


@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "ok"})

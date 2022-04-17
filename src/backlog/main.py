from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from mongoengine import connect
from mongoengine.connection import get_connection

from .settings import settings

connect(
    db=settings.mongodb_database,
    host=settings.mongodb_hostname,
    username=settings.mongodb_username,
    password=settings.mongodb_password.get_secret_value(),
    authentication_source=settings.mongodb_database,
)

app = FastAPI(title="🐻 Backlog tracker", version="0.1.0", debug=settings.debug)


@app.get("/readyz", status_code=status.HTTP_200_OK)
async def health_probe():
    get_connection().admin.command("ping")
    return JSONResponse(status_code=status.HTTP_200_OK)


@app.get("/livez", status_code=status.HTTP_200_OK)
async def liveness_probe():
    return JSONResponse(status_code=status.HTTP_200_OK)

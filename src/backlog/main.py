from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from mongoengine import connect
from mongoengine.connection import get_connection

from .epics import router as epics_router
from .settings import settings

connect(
    db=settings.mongodb_database,
    host=settings.mongodb_hostname,
    username=settings.mongodb_username,
    password=settings.mongodb_password.get_secret_value(),
    authentication_source=settings.mongodb_database,
)

app = FastAPI(
    title="🐻 Backlog tracker", version="0.1.0", debug=settings.debug, prefix="/v1/"
)


@app.get("/readyz", status_code=status.HTTP_200_OK, tags=["k8s"])
async def health_probe():
    get_connection().admin.command("ping")
    return JSONResponse(status_code=status.HTTP_200_OK)


@app.get("/livez", status_code=status.HTTP_200_OK, tags=["k8s"])
async def liveness_probe():
    return JSONResponse(status_code=status.HTTP_200_OK)


app.include_router(epics_router, prefix="/epics", tags=["epics"])

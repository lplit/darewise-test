from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from mongoengine import connect
from mongoengine.connection import get_connection

from backlog.routers.bugs import router as bugs_router
from backlog.routers.epics import router as epics_router
from backlog.routers.log import router as backlog_router
from backlog.routers.tasks import router as tasks_router
from backlog.settings import settings

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


app.include_router(bugs_router, prefix="/v1/bugs", tags=["bugs"])
app.include_router(epics_router, prefix="/v1/epics", tags=["epics"])
app.include_router(tasks_router, prefix="/v1/tasks", tags=["tasks"])
app.include_router(backlog_router, prefix="/v1/backlog", tags=["backlog"])

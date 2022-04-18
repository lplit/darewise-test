import logging

from fastapi import APIRouter, HTTPException, status
from mongoengine import DoesNotExist

from backlog.models import EpicInDB
from backlog.routers.epics import get_epics

router: APIRouter = APIRouter()
logger = logging.getLogger(__name__)


@router.delete(
    "/{task_id}",
    description="Delete a Task",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Epic not found"}},
)
def delete_task(task_id: str):
    try:
        EpicInDB.objects(Tasks__in=[task_id]).update(pull__Tasks=task_id)
        return get_epics()
    except DoesNotExist:
        logger.error(f"Task {task_id} does not exist")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} does not exist",
        )

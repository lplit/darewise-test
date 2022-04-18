import logging

from fastapi import APIRouter, HTTPException, status
from mongoengine import DoesNotExist

from backlog.models import EpicInDB
from backlog.routers.epics import get_epics

router: APIRouter = APIRouter()
logger = logging.getLogger(__name__)


@router.delete(
    "/{bug_id}",
    description="Delete a Bug",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Epic not found"}},
)
def delete_task(bug_id: str):
    try:
        EpicInDB.objects(Bugs__in=[bug_id]).update(pull__Bugs=bug_id)
        return get_epics()
    except DoesNotExist:
        logger.error(f"Task {bug_id} does not exist")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {bug_id} does not exist",
        )

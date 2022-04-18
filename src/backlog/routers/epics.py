import logging

from fastapi import APIRouter, HTTPException, status
from mongoengine import DoesNotExist, NotUniqueError

from backlog.models import Epic, EpicInDB, EpicStatus

"""
Manages epics and their routes

Possible states for an epic are:
"wip": "Contains any task or if any of its linked epics are wip",
"pending_validation": "all tasks are done (removed)"
                    + Bugs are pending"
                    + "or any Epics are 'pending_validation'"
                    + "and no Epics are 'wip'",
"completed": "there is no remaining tasks"
                    + "there is no remaining Bugs"
                    + "and all Epics are 'completed'",

"""


def check_any_linked_epics_are_status(*, epic: Epic, status: EpicStatus) -> bool:
    """Checks if any of the `epic.epics` are of the desired `status`"""
    for linked_epic in epic.epics:
        if get_epic_status(linked_epic) == status:
            return True
    return False


def check_all_linked_epics_are_status(*, epic: Epic, status: EpicStatus) -> bool:
    """Checks if all the `epic.epics` are of the desired `status`"""
    for linked_epic in epic.epics:
        if get_epic_status(linked_epic) != status:
            return False
    return True


def check_none_linked_epics_are_status(*, epic: Epic, status: EpicStatus) -> bool:
    """Checks if none of the `epic.epics` are of the desired `status`"""
    for linked_epic in epic.epics:
        if get_epic_status(linked_epic) == status:
            return False
    return True


def get_epic_status(epic: Epic) -> EpicStatus:
    """Determines an Epic's status, based on its tasks and epics"""

    if len(epic.tasks) > 0 or check_any_linked_epics_are_status(
        epic=epic, status=EpicStatus.WIP
    ):
        return EpicStatus.WIP

    if (
        len(epic.tasks) == 0
        and len(epic.bugs) == 0
        and check_all_linked_epics_are_status(epic=epic, status=EpicStatus.COMPLETED)
    ):
        return EpicStatus.COMPLETED

    if (len(epic.tasks) == 0 and len(epic.bugs) > 0) or (
        check_none_linked_epics_are_status(epic=epic, status=EpicStatus.PENDING)
        and check_none_linked_epics_are_status(epic=epic, status=EpicStatus.WIP)
    ):
        return EpicStatus.PENDING

    return EpicStatus.UNKNOWN


router: APIRouter = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/",
    summary="List all epics and their status",
    response_model=list[Epic],
)
def get_epics():
    """
    Returns a list of all epics and their status
    """
    return [Epic.from_orm(epic) for epic in EpicInDB.objects]


@router.post(
    "/",
    summary="Create an epic",
    response_model=Epic,
    responses={
        status.HTTP_409_CONFLICT: {"description": "Duplicate epic name, must be unique"}
    },
    status_code=status.HTTP_201_CREATED,
)
def create_epic(epic: Epic) -> EpicInDB:
    try:
        logger.info(f"Creating epic {epic}")
        epic_in_db = EpicInDB(**epic.dict())
        epic_in_db.save()
        return epic_in_db
    except NotUniqueError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Epic {epic.epic_id} already exists",
        )


@router.get(
    "/export",
    summary="Export all epics and their tasks",
    response_model=dict[str, dict],
)
def export_backlog() -> dict[str, dict]:
    """
    Returns a list of all epics and their tasks
    """
    ret: dict[str, dict] = {}
    for epic in EpicInDB.objects:
        epic = Epic.from_orm(epic)
        ret[epic.epic_id] = Epic.from_orm(epic).dict(exclude={"epic_id"}, by_alias=True)
    return ret


@router.get(
    "/{epic_id}",
    summary="Get an epic by id",
    response_model=Epic,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Epic not found"}},
)
def get_epic(epic_id: str) -> Epic:
    """
    Returns an epic by its id
    """
    try:
        return EpicInDB.objects.get(epic_id=epic_id)
    except DoesNotExist:
        logger.error(f"Epic {epic_id} does not exist")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )


@router.put(
    "/{epic_id}",
    summary="Update an Epic",
    response_model=Epic,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Epic not found"}},
)
def update_epic(epic_id: str, epic: Epic) -> Epic:
    """
    Updates an epic by its id
    """
    try:
        epic_in_db = EpicInDB.objects.get(epic_id=epic_id)
        epic_in_db.update(**epic.dict())
        epic_in_db.save()
        return Epic.from_orm(epic_in_db)
    except DoesNotExist:
        logger.error(f"Epic {epic_id} does not exist")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )


@router.patch(
    "/{epic_id}/bugs",
    summary="Update an Epic's status",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Epic not found"}},
)
def update_epic_bugs(epic_id: str, bugs: list[str]) -> Epic:
    """
    Updates an epic's bugs
    """
    try:
        epic_in_db = EpicInDB.objects.get(epic_id=epic_id)
        epic_in_db.bugs = bugs
        epic_in_db.save()
        return Epic.from_orm(epic_in_db)
    except DoesNotExist:
        logger.error(f"Epic {epic_id} does not exist")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

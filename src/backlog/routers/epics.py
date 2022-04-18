import logging

from fastapi import APIRouter, HTTPException, status
from mongoengine import DoesNotExist, NotUniqueError

from backlog.models import Epic, EpicInDB, EpicStatus, InputEpic

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
    for linked_epic in epic.Epics:
        if get_epic_status(linked_epic) == status:
            return True
    return False


def check_all_linked_epics_are_status(*, epic: Epic, status: EpicStatus) -> bool:
    """Checks if all the `epic.epics` are of the desired `status`"""
    for linked_epic in epic.Epics:
        if get_epic_status(linked_epic) != status:
            return False
    return True


def check_none_linked_epics_are_status(*, epic: Epic, status: EpicStatus) -> bool:
    """Checks if none of the `epic.epics` are of the desired `status`"""
    for linked_epic in epic.Epics:
        if get_epic_status(linked_epic) == status:
            return False
    return True


def get_epic_status(epic: Epic) -> EpicStatus:
    """Determines an Epic's status, based on its tasks and epics"""

    if len(epic.Tasks) > 0 or check_any_linked_epics_are_status(
        epic=epic, status=EpicStatus.WIP
    ):
        return EpicStatus.WIP

    if (
        len(epic.Tasks) == 0
        and len(epic.Bugs) == 0
        and check_all_linked_epics_are_status(epic=epic, status=EpicStatus.COMPLETED)
    ):
        return EpicStatus.COMPLETED

    if (len(epic.Tasks) == 0 and len(epic.Bugs) > 0) or (
        check_none_linked_epics_are_status(epic=epic, status=EpicStatus.PENDING)
        and check_none_linked_epics_are_status(epic=epic, status=EpicStatus.WIP)
    ):
        return EpicStatus.PENDING

    return EpicStatus.UNKNOWN


def get_epic_bugs(epic: Epic) -> set[str]:
    """Returns a list of bugs for an Epic"""
    return_set: set[str] = set()
    for bug in epic.Bugs:
        return_set.add(bug)

    for linked_epic in epic.Epics:
        for bug in linked_epic.Bugs:
            return_set.add(bug)
    return return_set


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
    response_model=list[Epic],
    responses={
        status.HTTP_409_CONFLICT: {"description": "Duplicate epic name, must be unique"}
    },
    status_code=status.HTTP_201_CREATED,
)
def create_epic(epic: InputEpic) -> list[Epic]:
    try:
        epics_references: list[EpicInDB] = []
        for linked_epic in epic.Epics:
            try:
                referenced_epic: EpicInDB = EpicInDB.objects.get(epic_id=linked_epic)
                epics_references.append(referenced_epic)
            except DoesNotExist:
                logger.error(
                    f"Epic {epic.epic_id} is trying to link with {linked_epic},"
                    + " which does not exist. Create it first."
                )
                continue
        epic_base: EpicInDB = EpicInDB(**epic.dict(exclude={"Epics"}))
        epic_base.Epics = epics_references
        epic_base.save()
        return [Epic.from_orm(epic) for epic in EpicInDB.objects]
    except NotUniqueError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Epic {epic.epic_id} already exists",
        )


@router.post(
    "/{epic_id}",
    summary="Replace Epic's tasks and bugs",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Epic not found"}},
    response_model=Epic,
)
def update_epic(epic_id: str, epic: Epic) -> Epic:
    """
    Updates an epic, use to update tasks and bugs.
    Replaces the Epic's tasks and bugs.
    """
    try:
        EpicInDB.objects(epic_id=epic_id).update(
            set__Tasks=epic.Tasks, set__Bugs=epic.Bugs
        )
        return EpicInDB.objects.get(epic_id=epic.epic_id)
    except DoesNotExist:
        logger.error(f"Epic {epic.epic_id} does not exist")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )


@router.get(
    "/{epic_id}/bugs",
    summary="Return all Bugs and all linked Epics' bugs",
    response_model=list[str],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Epic not found"}},
)
def get_bugs(epic_id: str) -> set[str]:
    """
    Returns an epic by its id
    """
    try:
        epic: Epic = Epic.from_orm(EpicInDB.objects.get(epic_id=epic_id))
        return get_epic_bugs(epic)
    except DoesNotExist:
        logger.error(f"Epic {epic_id} does not exist")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

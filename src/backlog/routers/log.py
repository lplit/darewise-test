import logging

from fastapi import APIRouter, Body, HTTPException, status
from mongoengine import NotUniqueError

from backlog.models import Epic, EpicInDB, InputEpic
from backlog.routers.epics import create_epic

router: APIRouter = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/",
    summary="Export backlog",
    response_model=dict[str, dict],
)
def export_backlog() -> dict[str, dict]:
    """
    Returns a list of all epics and their tasks
    """
    ret: dict[str, dict] = {}
    for epic in EpicInDB.objects:
        epic = Epic.from_orm(epic)
        linked_epics_ids: list[str] = []
        for linked_epic in epic.Epics:
            linked_epics_ids.append(linked_epic.epic_id)
        return_epic: dict = Epic.from_orm(epic).dict(exclude={"epic_id"}, by_alias=True)
        return_epic["Epics"] = linked_epics_ids
        ret[epic.epic_id] = return_epic
    return ret


@router.post(
    "/",
    summary="Imports backlog from a json and merge with existing",
    status_code=status.HTTP_201_CREATED,
)
def import_backlog(
    backlog: dict[str, dict] = Body(
        ...,
        example={
            "EpicA": {"Tasks": ["TaskA1", "TaskA2"], "Bugs": [], "Epics": ["EpicB"]},
            "EpicB": {"Tasks": ["TaskB1", "TaskB2"], "Bugs": ["BugB1"], "Epics": [""]},
            "EpicC": {"Tasks": [], "Bugs": [], "Epics": []},
            "EpicD": {"Tasks": [], "Bugs": [], "Epics": ["EpicC"]},
            "EpicE": {"Tasks": [], "Bugs": ["BugE1"], "Epics": []},
        },
    )
) -> dict[str, dict]:
    for k, v in backlog.items():
        try:
            tmp_dict: dict = {"epic_id": k, **v}
            epic = InputEpic.parse_obj(tmp_dict)
            create_epic(epic)
            logger.debug(f"Created epic is {epic.dict()}")
        except NotUniqueError:
            logger.error(f"Epic {epic.epic_id} already exists, skipping")
            continue
        except HTTPException as e:
            if e.status_code != status.HTTP_409_CONFLICT:
                logger.error("Something unexpected happened")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Item not found",
                )
            continue

    return export_backlog()

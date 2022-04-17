from __future__ import annotations  # For self-referencing pydantic models

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

# {
#     "wip": "Contains any task or if any of its linked epics are wip",
#     "pending_validation": "all tasks are done (removed)"
#                       + Bugs are pending"
#                       + "or any Epics are 'pending_validation'"
#                       + "and no Epics are 'wip'",
#     "completed": "there is no remaining tasks"
#                       + "there is no remaining Bugs"
#                       + "and all Epics are 'completed'",
#     "blocked": "there are no remaining tasks"
#                       + "and there are remaining tasks in linked Epics",
# }


class EpicStatus(Enum):
    WIP = "work in progress"
    PENDING = "pending validation"
    COMPLETED = "completed"
    UNKNOWN = "unknown"


class Epic(BaseModel):
    id: str = Field(None, alias="_id")
    tasks: List[str] = Field([], description="Tasks linked to this epic", alias="Tasks")
    bugs: List[str] = Field([], description="Bugs linked to this epic", alias="Bugs")
    epics: List[Epic] = Field(
        [], description="Epics linked to this epic", alias="Epics"
    )


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

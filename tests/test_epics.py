import logging

from backlog.routers.epics import (
    EpicStatus,
    check_all_linked_epics_are_status,
    check_any_linked_epics_are_status,
    check_none_linked_epics_are_status,
    get_epic_bugs,
    get_epic_status,
)

logger = logging.getLogger(__name__)


def test_epic_A_should_be_wip(epic_A):
    assert get_epic_status(epic_A) == EpicStatus.WIP


def test_epic_B_should_be_wip(epic_B):
    assert get_epic_status(epic_B) == EpicStatus.WIP


def test_epic_C_should_be_completed(epic_C):
    assert get_epic_status(epic_C) == EpicStatus.COMPLETED


def test_epic_D_should_be_completed(epic_D):
    assert get_epic_status(epic_D) == EpicStatus.COMPLETED


def test_epic_E_should_be_pending(epic_E):
    assert get_epic_status(epic_E) == EpicStatus.PENDING


def test_epic_D_linked_epics_should_be_Completed(epic_D):
    assert check_all_linked_epics_are_status(epic=epic_D, status=EpicStatus.COMPLETED)


def test_epic_A_linked_epics_should_be_WIP(epic_A):
    assert check_all_linked_epics_are_status(epic=epic_A, status=EpicStatus.WIP)


def test_epic_A_no_linked_epics_should_be_COMPLETE(epic_A):
    assert check_none_linked_epics_are_status(epic=epic_A, status=EpicStatus.COMPLETED)


def test_epic_A_any_linked_epics_should_be_COMPLETE(epic_D):
    assert check_any_linked_epics_are_status(epic=epic_D, status=EpicStatus.COMPLETED)


def test_get_epic_bugs_should_return_non_empty_set(epic_F):
    assert len(get_epic_bugs(epic_F)) == 4

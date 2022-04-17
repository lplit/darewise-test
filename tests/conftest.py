from typing import Any, Dict

import pytest

from backlog.epics import Epic

example_backlog: Dict[str, Any] = {
    "EpicA": {"Tasks": ["TaskA1", "TaskA2"], "Bugs": [], "Epics": ["EpicB"]},
    "EpicB": {"Tasks": ["TaskB1", "TaskB2"], "Bugs": ["BugB1"], "Epics": [""]},
    "EpicC": {"Tasks": [], "Bugs": [], "Epics": []},
    "EpicD": {"Tasks": [], "Bugs": [], "Epics": ["EpicC"]},
    "EpicE": {"Tasks": [], "Bugs": ["BugE1"], "Epics": []},
}


# Status: Pending Validation
epic_e: Dict = {"id": "EpicE", "Tasks": [], "Bugs": ["BugE1"], "Epics": []}

# Status: Completed
epic_c: Dict = {"id": "EpicC", "Tasks": [], "Bugs": [], "Epics": []}

# Status: Completed
epic_d: Dict = {"id": "EpicD", "Tasks": [], "Bugs": [], "Epics": [epic_c]}

# Status: WIP
epic_b: Dict = {
    "id": "EpicB",
    "Tasks": ["TaskB1", "TaskB2"],
    "Bugs": ["BugB1"],
    "Epics": [""],
}

# Status WIP
epic_a: Dict = {
    "id": "EpicA",
    "Tasks": ["TaskA1", "TaskA2"],
    "Bugs": [],
    "Epics": [epic_b],
}


@pytest.fixture(scope="function")
def epic_A() -> Epic:
    return Epic(**epic_a)


@pytest.fixture(scope="function")
def epic_B() -> Epic:
    return Epic(**epic_b)


@pytest.fixture(scope="function")
def epic_C() -> Epic:
    return Epic(**epic_c)


@pytest.fixture(scope="function")
def epic_D() -> Epic:
    return Epic(**epic_d)


@pytest.fixture(scope="function")
def epic_E() -> Epic:
    return Epic(**epic_e)
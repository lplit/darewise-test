from __future__ import annotations  # For self-referencing pydantic models

from enum import Enum
from typing import List

from mongoengine import Document, ListField, ReferenceField, StringField
from pydantic import BaseModel, Field


class EpicStatus(Enum):
    WIP = "work in progress"
    PENDING = "pending validation"
    COMPLETED = "completed"
    UNKNOWN = "unknown"


class InputEpic(BaseModel):
    epic_id: str = Field(...)
    Tasks: List[str] = Field([], description="Tasks linked to this epic", alias="Tasks")
    Bugs: List[str] = Field([], description="Bugs linked to this epic", alias="Bugs")
    Epics: List[str] = Field([], description="Epics linked to this epic", alias="Epics")

    class Config:
        schema_extra = {
            "example": {
                "epic_id": "EpicA1",
                "Tasks": ["TaskA1", "TaskC2"],
                "Bugs": ["BugA1", "BugC2"],
                "Epics": [],
            }
        }


class Epic(BaseModel):
    """Field aliases used to comply with the PascalCase specs sheet"""

    epic_id: str = Field(...)
    Tasks: List[str] = Field([], description="Tasks linked to this epic", alias="Tasks")
    Bugs: List[str] = Field([], description="Bugs linked to this epic", alias="Bugs")
    Epics: List[Epic] = Field(
        [], description="Epics linked to this epic", alias="Epics"
    )

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "epic_id": "EpicA1",
                "Tasks": ["TaskA1", "TaskC2"],
                "Bugs": ["BugA1", "BugC2"],
                "Epics": [],
            }
        }


class EpicInDB(Document):
    epic_id: str = StringField(unique=True, required=True)
    Tasks = ListField(default=[])
    Bugs = ListField(default=[])
    Epics = ListField(ReferenceField("EpicInDB"), default=[])


class Bug(BaseModel):
    bug_id: str = Field(...)
    epic_id: str = Field(...)
    content: str = Field()

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "bug_id": "BugA1",
                "epic_id": "EpicA1",
                "content": "Lorem ipsum dolor sit amet",
            }
        }


class BugInDB(Document):
    bug_id: str = StringField(unique=True, required=True)
    epic: Epic = ReferenceField("EpicInDB")
    content: str = StringField(default="Lorem ipsum dolor sit amet")


class Task(BaseModel):
    task_id: str = Field(...)
    epic_id: str = Field(...)
    content: str = Field(default="Lorem ipsum dolor sit amet")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "task_id": "TaskA1",
                "epic_id": "EpicA1",
                "content": "Lorem ipsum dolor sit amet",
            }
        }


class TaskInDB(Document):
    task_id: str = StringField(unique=True, required=True)
    epic_id: Epic = ReferenceField("EpicInDB")
    content: str = StringField(default="Lorem ipsum dolor sit amet")


class BacklogEntry(BaseModel):
    status: EpicStatus = Field()
    epic: Epic = Field()

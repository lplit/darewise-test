from __future__ import annotations  # For self-referencing pydantic models

import uuid
from enum import Enum
from typing import List

from mongoengine import Document, ListField, ReferenceField, StringField
from pydantic import BaseModel, Field


class EpicStatus(Enum):
    WIP = "work in progress"
    PENDING = "pending validation"
    COMPLETED = "completed"
    UNKNOWN = "unknown"


class Epic(BaseModel):
    """Field aliases used to comply with the PascalCase specs sheet"""

    epic_id: str = Field(...)
    tasks: List[str] = Field([], description="Tasks linked to this epic", alias="Tasks")
    bugs: List[str] = Field([], description="Bugs linked to this epic", alias="Bugs")
    epics: List[Epic] = Field(
        [], description="Epics linked to this epic", alias="Epics"
    )

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "epic_id": "EpicA1",
                "tasks": ["TaskA1", "TaskC2"],
                "bugs": ["BugA1", "BugC2"],
                "epics": [],
            }
        }


class EpicInDB(Document):
    epic_id: str = StringField(unique=True)
    tasks = ListField()
    bugs = ListField()
    epics = ListField(ReferenceField("EpicInDB"))

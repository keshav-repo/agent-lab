import math
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


def _is_blank(value) -> bool:
    if value is None or value == "":
        return True
    return isinstance(value, float) and math.isnan(value)

class DuplicateClassification(StrEnum):
    DUPLICATE = "DUPLICATE"
    NEW = "NEW"

class LearningEntity(BaseModel):
    id: int | None = None
    text: str

    category: str
    subcategory: str | None = None
    topic: str | None = None
    subtopic: str | None = None
    concept: str | None = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags(cls, value):
        if _is_blank(value):
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [tag.strip() for tag in value.split(",") if tag.strip()]
        return value

class LearningMetadata(BaseModel):
    category: str
    subcategory: str | None = None
    topic: str | None = None
    subtopic: str | None = None
    concept: str | None = None

class NearestLearningItem(BaseModel):
    id: str
    document: str
    distance: float

class DuplicateCheckResult(BaseModel):
    classification: DuplicateClassification
    matched_id: str | None = None
    canonical_question: str = ""
    reason: str = ""

    @field_validator("matched_id", mode="before")
    @classmethod
    def coerce_matched_id(cls, value):
        if value is None:
            return None
        return str(value)

class DuplicateCheck(BaseModel):
    item: LearningEntity
    candidates: list[NearestLearningItem]

class Alias(BaseModel):
    aliasId: int | None = None
    alias: str
    parentId: int

class LearningEntityAliasCount(LearningEntity):
    aliasCount: int | None = None

class LearningEntityWithAliases(LearningEntity):
    aliases: list[str] = Field(default_factory=list)

    @field_validator("aliases", mode="before")
    @classmethod
    def parse_aliases(cls, value):
        if _is_blank(value):
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [
                line.lstrip("•").strip()
                for line in value.splitlines()
                if line.strip()
            ]
        return value

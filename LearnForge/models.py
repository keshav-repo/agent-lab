from enum import StrEnum

from pydantic import BaseModel, Field, field_validator

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

class LearningEntityAlias(LearningEntity):
    aliasCount: int | None = None

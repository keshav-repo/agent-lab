from pydantic import BaseModel, Field

class LearningEntity(BaseModel):
    id: int | None = None
    text: str

    category: str
    subcategory: str | None = None
    topic: str | None = None
    subtopic: str | None = None
    concept: str | None = None
    tags: list[str] = Field(default_factory=list)


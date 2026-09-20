import json

from models import LearningEntity


def to_learning_entity(raw: str) -> LearningEntity:
    return LearningEntity.model_validate_json(raw)


def parse_learning_items(raw: str) -> list[LearningEntity]:
    payload = json.loads(raw)
    return [
        to_learning_entity(json.dumps(item))
        for item in payload["learning_items"]
    ]


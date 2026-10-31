import json
from pathlib import Path

from Constants import BASE_PATH
from ExcelUtils import readExcel
from fs_utils import list_files
from models import LearningEntity, LearningEntityWithAliases


def to_learning_entity(raw: str) -> LearningEntity:
    return LearningEntity.model_validate_json(raw)

def parse_learning_items(raw: str) -> list[LearningEntity]:
    payload = json.loads(raw)
    return [
        to_learning_entity(json.dumps(item))
        for item in payload["learning_items"]
    ]

def _read_entities_from_excel() -> list[LearningEntityWithAliases]:
    entities = []
    base_dir = Path(BASE_PATH)
    for file_name in list_files(base_dir):
        if not file_name.endswith(".xlsx"):
            continue
        df = readExcel(str(base_dir / file_name), "Learning Entities")
        # Cast to object first: empty columns are float64 and would keep NaN
        # (not None), which fails validation for optional string fields.
        df = df.astype(object).where(df.notna(), None)
        records = df.to_dict(orient="records")
        entities.extend(
            LearningEntityWithAliases.model_validate(row) for row in records
        )
    return entities

# This will read the downloaded excel files which will be used to update metadata
def readEntry_fromExcel() -> list[LearningEntityWithAliases]:
    return _read_entities_from_excel()

def readLearningEntry_fromExcel() -> list[LearningEntityWithAliases]:
    return _read_entities_from_excel()


import json
import sqlite3
from pathlib import Path

from models import LearningEntity

DB_PATH = Path(__file__).resolve().parent / "knowledge.db"
conn = sqlite3.connect(DB_PATH)

CREATE_LEARNING_ENTITIES = """
CREATE TABLE IF NOT EXISTS learning_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT,
    topic TEXT,
    subtopic TEXT,
    concept TEXT,
    tags JSON NOT NULL DEFAULT '[]'
)
"""

conn.execute(CREATE_LEARNING_ENTITIES)
conn.commit()

def upsert_learning_entity(entity: LearningEntity) -> LearningEntity:
    cursor = conn.execute(
        """
        INSERT INTO learning_entities (
            id, text, category, subcategory, topic, subtopic, concept, tags
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            text = excluded.text,
            category = excluded.category,
            subcategory = excluded.subcategory,
            topic = excluded.topic,
            subtopic = excluded.subtopic,
            concept = excluded.concept,
            tags = excluded.tags
        """,
        (
            entity.id,
            entity.text,
            entity.category,
            entity.subcategory,
            entity.topic,
            entity.subtopic,
            entity.concept,
            json.dumps(entity.tags),
        ),
    )
    conn.commit()
    return entity.model_copy(update={"id": entity.id or cursor.lastrowid})


def _to_learning_entity(row) -> LearningEntity:
    return LearningEntity(
        id=row[0],
        text=row[1],
        category=row[2],
        subcategory=row[3],
        topic=row[4],
        subtopic=row[5],
        concept=row[6],
        tags=json.loads(row[7] or "[]"),
    )


def get_learning_entity_by_id(entity_id: int) -> LearningEntity | None:
    row = conn.execute(
        """
        SELECT id, text, category, subcategory, topic, subtopic, concept, tags
        FROM learning_entities
        WHERE id = ?
        """,
        (entity_id,),
    ).fetchone()
    if row is None:
        return None
    return _to_learning_entity(row)


def get_all_learning_entities() -> list[LearningEntity]:
    rows = conn.execute(
        """
        SELECT id, text, category, subcategory, topic, subtopic, concept, tags
        FROM learning_entities
        ORDER BY id
        """
    ).fetchall()
    return [_to_learning_entity(row) for row in rows]



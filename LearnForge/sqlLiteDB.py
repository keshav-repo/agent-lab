import json
import sqlite3
import uuid

from models import LearningEntity

conn = sqlite3.connect("knowledge.db")

CREATE_LEARNING_ENTITIES = """
CREATE TABLE IF NOT EXISTS learning_entities (
    id TEXT PRIMARY KEY,
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
    entity_id = entity.id or str(uuid.uuid4())
    conn.execute(
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
            entity_id,
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
    return entity.model_copy(update={"id": entity_id})

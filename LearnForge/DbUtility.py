import threading

from models import LearningEntity, LearningEntityWithAliases, LearningMetadata, NearestLearningItem
from sqlLiteDB import update_metadata, upsert_learning_entity
from vectorDb import get_learning_collection

save_in_db_lock = threading.Lock()

def build_metadata(item: LearningEntity) -> LearningMetadata:
    return LearningMetadata(
        category=item.category,
        subcategory=item.subcategory,
        topic=item.topic,
        subtopic=item.subtopic,
        concept=item.concept,
    )

def find_nearest_learning_item(entity: LearningEntity) -> list[NearestLearningItem]:
    results = get_learning_collection().query(
        query_texts=[entity.text],
        n_results=5,
        include=["documents", "metadatas", "distances"]
    )

    if not results["ids"] or not results["ids"][0]:
        return []

    return [
        NearestLearningItem(
            id=item_id,
            document=document,
            distance=distance,
        )
        for item_id, document, distance in zip(
            results["ids"][0],
            results["documents"][0],
            results["distances"][0],
        )
    ]

def save_in_db(entity: LearningEntity):
    with save_in_db_lock:
        # Insert in SQLite
        entity = upsert_learning_entity(entity)
        # Insert in ChromaDB
        metadata = build_metadata(entity).model_dump(exclude_none=True)
        get_learning_collection().add(
            ids=str(entity.id),
            documents=entity.text,
            metadatas=metadata,
        )

def update_metadata_in_db(entities: list[LearningEntityWithAliases]):
    with save_in_db_lock:
        update_metadata(entities)

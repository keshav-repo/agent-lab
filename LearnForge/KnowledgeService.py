from pathlib import Path
import shutil

from Constants import BASE_PATH, SIMILARITY_THRESHOLD
from fs_utils import list_files, readFile
from helper import parse_learning_items
from models import LearningEntity, LearningMetadata
from sqlLiteDB import upsert_learning_entity
from vectorDb import learningCollection

def build_metadata(item: LearningEntity) -> LearningMetadata:
    return LearningMetadata(
        category=item.category,
        subcategory=item.subcategory,
        topic=item.topic,
        subtopic=item.subtopic,
        concept=item.concept,
    )

def find_similar_learning_item(entity: LearningEntity):
    results = learningCollection.query(
        query_texts=[entity.text],
        n_results=1,
        include=["documents", "metadatas", "distances"]
    )

    if not results["ids"] or not results["ids"][0]:
        return None

    distance = results["distances"][0][0]

    if distance <= SIMILARITY_THRESHOLD:
        return {
            "id": results["ids"][0][0],
            "document": results["documents"][0][0],
            "metadata": results["metadatas"][0][0],
            "distance": distance
        }

    return None

def UploadLearningItems():
    for file_name in list_files(BASE_PATH):
        if not file_name.endswith('.json'):
            continue

        content = readFile(BASE_PATH, file_name)
        learning_items = parse_learning_items(content)

        for item in learning_items:
            entity = upsert_learning_entity(item)

            similar_item = find_similar_learning_item(item)

            if similar_item and similar_item['distance'] == 0:
                print('exact item')
                continue

            if similar_item and similar_item['distance'] <= SIMILARITY_THRESHOLD:
                print("Similar learning item found")
                print(f"Distance : {similar_item['distance']}")

            # chroma db
            id = entity.id
            metadata = build_metadata(entity)
            learningCollection.add(
                ids=id,
                documents=entity.text,
                metadatas=metadata,
            )

    # Delete all files after parsing
    for path in Path(BASE_PATH).iterdir():
        if path.is_file():
            path.unlink()

def UploadFiles(file_paths):
    destination = Path(BASE_PATH)
    destination.mkdir(parents=True, exist_ok=True)

    for file_path in file_paths:
        source = Path(file_path)
        if not source.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
        shutil.copy2(source, destination / source.name)

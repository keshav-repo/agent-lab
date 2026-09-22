from pathlib import Path

import chromadb

CHROMA_PATH = Path(__file__).resolve().parent / "data" / "chroma"

client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)

learningCollection = client.get_or_create_collection(
    name="learning_items"
)

from pathlib import Path

import chromadb

CHROMA_PATH: Path | None = None
client = None
learningCollection = None


def init_chroma(workspace_dir: str | Path):
    global CHROMA_PATH, client, learningCollection
    workspace_dir = Path(workspace_dir)
    CHROMA_PATH = workspace_dir / "chroma"
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    learningCollection = client.get_or_create_collection(name="learning_items")
    return learningCollection


def get_learning_collection():
    if learningCollection is None:
        raise RuntimeError("Chroma is not initialized. Call init_chroma() first.")
    return learningCollection

from pathlib import Path
import shutil

from Constants import BASE_PATH
from fs_utils import list_files, readFile
from helper import parse_learning_items
from sqlLiteDB import upsert_learning_entity
from vectorDb import learningCollection

def UploadLearningItems():
    for file_name in list_files(BASE_PATH):
        if not file_name.endswith('.json'):
            continue

        content = readFile(BASE_PATH, file_name)
        learning_items = parse_learning_items(content)

        for item in learning_items:
            upsert_learning_entity(item)

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

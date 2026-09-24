import os
import shutil
from pathlib import Path

from Constants import BASE_PATH
from logger import L


def list_files(directory="."):
    return os.listdir(directory)

def readFile(base_path, file_name):
    file_path = os.path.join(base_path, file_name)
    with open(file_path, 'r') as file:
        content = file.read()
    return content

def UploadFiles(file_paths):
    destination = Path(BASE_PATH)
    destination.mkdir(parents=True, exist_ok=True)

    for file_path in file_paths:
        source = Path(file_path)
        if not source.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
        shutil.copy2(source, destination / source.name)
    L.info(f"Uploaded files")

def delete_all_files(directory):
    # Delete all files after parsing
    for path in Path(directory).iterdir():
        if path.is_file():
            path.unlink()

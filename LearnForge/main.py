from fs_utils import list_files, readFile
from helper import parse_learning_items
from vectorDb import learningCollection

base_path = '/Users/keshavkumar/learn26/agent-lab/LearnForge/jsons'


def build_metadata(item):
    metadata = item.model_dump(exclude={"id", "text", "tags"}, exclude_none=True)
    if item.tags:
        metadata["tags"] = ", ".join(item.tags)
    return metadata


for file_name in list_files(base_path):
    if not file_name.endswith('.json'):
        continue

    content = readFile(base_path, file_name)
    learning_items = parse_learning_items(content)

    learningCollection.upsert(
        ids=[item.id or f'{file_name}:{index}' for index, item in enumerate(learning_items)],
        documents=[item.text for item in learning_items],
        metadatas=[build_metadata(item) for item in learning_items],
    )


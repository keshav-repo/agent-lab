from concurrent.futures import ThreadPoolExecutor, as_completed

from logger import L
from Agents.duplicate_detection_agent import check_duplicate
from models import DuplicateCheck, DuplicateClassification, LearningEntity

def find_items_to_save(items_for_duplicate_check: list[DuplicateCheck]) -> list[LearningEntity]:
    items_to_save: list[LearningEntity] = []

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(
                check_duplicate,
                duplicate_check.item.text,
                duplicate_check.candidates,
            ): duplicate_check.item
            for duplicate_check in items_for_duplicate_check
        }

        for future in as_completed(futures):
            item = futures[future]
            result = future.result()
            if result.classification != DuplicateClassification.DUPLICATE:
                items_to_save.append(item)
            else:
                L.info("Duplicate found, skipping item: %s", item.text)

    return items_to_save

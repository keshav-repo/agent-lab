from ExcelUtils import readExcel
from logger import L
from Agents.DublicateAgentOrchestrator import find_items_to_save
from Constants import BASE_PATH, DUPLICATE_DISTANCE_THRESHOLD, SIMILARITY_DISTANCE_THRESHOLD
from DbUtility import find_nearest_learning_item, save_in_db, update_metadata_in_db
from fs_utils import list_files, readFile, delete_all_files
from helper import parse_learning_items, readEntry_fromExcel, readLearningEntry_fromExcel
from models import DuplicateCheck, LearningEntityAliasCount, LearningEntity, LearningEntityWithAliases
from sqlLiteDB import get_LearningEntity_join_aliasCount, get_LearningEntity_join_alias_withIds


def processLearningItems(learning_items: list[LearningEntity]):
    items_for_duplicate_check = []
    items_to_save = []

    for item in learning_items:
        nearestItems = find_nearest_learning_item(item)
        if len(nearestItems) == 0:
            L.info("Found no nearest items for %s", item.text)
            items_to_save.append(item)
            continue

        first_Nearest_Item = nearestItems[0]
        distance = first_Nearest_Item.distance
        if (distance == 0):
            L.info("Exact match found, skipping item: %s", item.text)
            continue
        elif (distance <= DUPLICATE_DISTANCE_THRESHOLD):
            L.info("Below Dublicate Threashold, skipping item: %s", item.text)
            continue
        elif (distance <= SIMILARITY_DISTANCE_THRESHOLD):
            L.info("to check for dublicate: %s", item.text)
            items_for_duplicate_check.append(DuplicateCheck(item=item, candidates=nearestItems))
        else:
            L.info("new item found, distance greater than threshold")
            items_to_save.append(item)

    new_items = find_items_to_save(items_for_duplicate_check)
    items_to_save.extend(new_items)

    for item in items_to_save:
        save_in_db(item)

def UploadLearningItems():
    L.info("Upload Learning Items and process")
    for file_name in list_files(BASE_PATH):
        if not file_name.endswith('.json'):
            continue
        L.info("Processing file: %s", file_name)
        content = readFile(BASE_PATH, file_name)
        learning_items = parse_learning_items(content)
        processLearningItems(learning_items)

    # Delete all files after parsing
    delete_all_files(BASE_PATH)

def get_LearningItems() -> list[LearningEntityAliasCount]:
    L.info("Get Learning Items called")
    res =  get_LearningEntity_join_aliasCount()
    return res

def update_metadata_using_excel():
    L.info("Update Learning Metadata")
    entityList = readEntry_fromExcel()
    update_metadata_in_db(entityList)
    delete_all_files(BASE_PATH)

def upload_learning_entities_using_excel():
    L.info("Upload Learning Entities from Excel")
    entityList = readLearningEntry_fromExcel()
    processLearningItems(entityList)
    delete_all_files(BASE_PATH)

def get_pdf_content(selectedId: list[int]) -> list[LearningEntityWithAliases]:
   L.info("Get PDF content with selected ids")
   res = get_LearningEntity_join_alias_withIds(selectedId)
   return res

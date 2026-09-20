import chromadb

client = chromadb.PersistentClient(
    path="./data/chroma"
)

learningCollection = client.get_or_create_collection(
    name="learning_items"
)

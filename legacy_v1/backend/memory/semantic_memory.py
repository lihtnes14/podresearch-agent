import chromadb

CHROMA_PATH = "./chroma_db"

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_or_create_collection(
    name="podresearch_memory"
)


def add_memory(
    memory_id: str,
    text: str,
    metadata: dict | None = None,
):
    collection.upsert(
        ids=[memory_id],
        documents=[text],
        metadatas=[metadata or {}],
    )


def search_memory(
    query: str,
    n_results: int = 5,
    max_distance: float = 1.0,
):
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    memories = []

    for i in range(len(results["ids"][0])):

        distance = results["distances"][0][i]

        if distance > max_distance:
            continue

        memories.append(
            {
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": distance,
            }
        )


    return memories

def memory_exists(
    query: str,
    max_distance: float = 0.15,
) -> bool:

    results = collection.query(
        query_texts=[query],
        n_results=1,
    )

    if not results["distances"][0]:
        return False

    distance = results["distances"][0][0]

    return distance <= max_distance

def list_all_memories():

    results = collection.get(
        include=["documents", "metadatas"]
    )

    for i in range(len(results["ids"])):

        print()
        print("=" * 60)

        print("ID:")
        print(results["ids"][i])

        print("Metadata:")
        print(results["metadatas"][i])

        print("Document:")
        print(results["documents"][i])

def delete_memory(memory_id: str):
    collection.delete(ids=[memory_id])
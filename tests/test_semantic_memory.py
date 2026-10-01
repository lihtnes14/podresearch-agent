from memory.semantic_memory import (
    add_memory,
    search_memory,
)


add_memory(
    memory_id="java_gosling",
    text="Java was designed by James Gosling at Sun Microsystems.",
    metadata={
        "topic": "Java",
        "source": "podcast",
    },
)


results = search_memory(
    "Who created Java?",
    n_results=3,
)


for result in results:
    print("=" * 50)
    print("ID:", result["id"])
    print("TEXT:", result["text"])
    print("METADATA:", result["metadata"])
    print("DISTANCE:", result["distance"])
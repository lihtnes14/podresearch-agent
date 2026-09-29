from memory.semantic_memory import (
    search_memory,
    add_memory,
    memory_exists,
)


def store_research_memory(
    session_id: str,
    research: list[dict],
):

    for i, result in enumerate(research):

        # Only store verified findings
        if result["status"] != "SUPPORTED":
            continue

        memory_text = (
            f"Claim: {result['claim']}\n"
            f"Finding: {result['explanation']}"
        )

        # Check for an existing similar memory
        if memory_exists(memory_text):

            print(
                "🧠 Memory already exists — skipping:"
            )
            print(
                f"   {result['claim']}"
            )

            continue

        memory_id = f"{session_id}_research_{i}"

        add_memory(
            memory_id=memory_id,
            text=memory_text,
            metadata={
                "session_id": session_id,
                "artifact_type": "research",
                "status": result["status"],
                "topic": result["claim"][:100],
            },
        )

        print(
            "🧠 New memory stored:"
        )
        print(
            f"   {result['claim']}"
        )


def retrieve_relevant_memory(
    query: str,
    current_session_id: str,
    n_results: int = 3,
) -> list[dict]:

    memories = search_memory(
        query=query,
        n_results=n_results,
        max_distance=1.0,
    )

    relevant_memories = []

    for memory in memories:

        memory_session_id = memory["metadata"].get(
            "session_id"
        )

        # Ignore memories without session information
        if memory_session_id is None:
            continue

        # Don't retrieve memories from the current session
        if memory_session_id == current_session_id:
            continue

        relevant_memories.append(
            {
                "text": memory["text"],
                "metadata": memory["metadata"],
                "distance": memory["distance"],
            }
        )

    return relevant_memories
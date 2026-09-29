from agents.memory_agent import retrieve_relevant_memory
from memory.semantic_memory import add_memory


add_memory(
    memory_id="session_a_java",
    text="Java was designed by James Gosling at Sun Microsystems.",
    metadata={
        "session_id": "session_a",
        "artifact_type": "research",
        "topic": "Java",
        "source": "Tavily",
    },
)


add_memory(
    memory_id="session_b_python",
    text="Python was created by Guido van Rossum.",
    metadata={
        "session_id": "session_b",
        "artifact_type": "research",
        "topic": "Python",
        "source": "Tavily",
    },
)


results = retrieve_relevant_memory(
    query="Who created Java?",
    current_session_id="session_c",
    n_results=3,
)


for result in results:
    print("=" * 50)
    print("TEXT:", result["text"])
    print("SESSION:", result["metadata"].get("session_id"))
    print("TYPE:", result["metadata"].get("artifact_type"))
    print("TOPIC:", result["metadata"].get("topic"))
    print("SOURCE:", result["metadata"].get("source"))
    print("DISTANCE:", result["distance"])
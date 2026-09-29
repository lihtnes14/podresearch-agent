import time
from uuid import uuid4

from graph.workflow import workflow


# ============================================================
# CONFIGURATION
# ============================================================

podcast_url = (
    "https://youtu.be/l9AzO1FMgM8"
    "?si=WUIBimKcuoU65Tx-"
)

session_id = str(uuid4())


# ============================================================
# INITIAL STATE
# ============================================================

initial_state = {
    "session_id": session_id,
    "podcast_url": podcast_url,

    "transcript": "",
    "analysis": {},
    "historical_context": [],
    "research": [],

    "article": {},
    "guardrail_result": {},
    "critique": {},

    "revision_count": 0,

    "loaded_artifacts": [],
}


# ============================================================
# START
# ============================================================

print()
print("=" * 60)
print("STARTING PODRESEARCH LANGGRAPH")
print("=" * 60)
print()

print(f"Session ID: {session_id}")
print(f"Podcast URL: {podcast_url}")

print()


# ============================================================
# WORKFLOW EXECUTION
# ============================================================

workflow_start = time.perf_counter()

final_state = initial_state.copy()


for event in workflow.stream(initial_state):

    for node_name, state_update in event.items():

        print()
        print("-" * 60)
        print(f"NODE COMPLETED: {node_name}")
        print("-" * 60)

        # Merge LangGraph's partial state update
        final_state.update(state_update)

        # ----------------------------------------------------
        # MEMORY NODE
        # ----------------------------------------------------

        if node_name == "memory":

            loaded_artifacts = state_update.get(
                "loaded_artifacts",
                []
            )

            print(
                "Loaded artifacts:",
                loaded_artifacts
            )

        # ----------------------------------------------------
        # MEMORY RETRIEVAL NODE
        # ----------------------------------------------------

        elif node_name == "memory_retrieval":

            historical_context = state_update.get(
                "historical_context",
                []
            )

            print(
                "Historical memories retrieved:",
                len(historical_context)
            )

        # ----------------------------------------------------
        # RESEARCH NODE
        # ----------------------------------------------------

        elif node_name == "research":

            research = state_update.get(
                "research",
                []
            )

            print(
                "Research results:",
                len(research)
            )

        # ----------------------------------------------------
        # WRITER NODE
        # ----------------------------------------------------

        elif node_name == "writer":

            article = state_update.get(
                "article",
                {}
            )

            if article:

                print(
                    "Article generated successfully."
                )

                print(
                    f"Title: {article.get('title', 'N/A')}"
                )

        # ----------------------------------------------------
        # GUARDRAIL NODE
        # ----------------------------------------------------

        elif node_name == "guardrail":

            guardrail_result = state_update.get(
                "guardrail_result",
                {}
            )

            passed = guardrail_result.get(
                "passed",
                False
            )

            print(
                "Guardrail passed:",
                passed
            )

            if not passed:

                violations = guardrail_result.get(
                    "violations",
                    []
                )

                print(
                    "Violations:",
                    len(violations)
                )

                for violation in violations:

                    print(
                        f"  → Type: {violation.get('type')}"
                    )

                    print(
                        f"    Severity: {violation.get('severity')}"
                    )

                    print(
                        f"    Explanation: "
                        f"{violation.get('explanation')}"
                    )

        # ----------------------------------------------------
        # CRITIC NODE
        # ----------------------------------------------------

        elif node_name == "critic":

            revision_count = state_update.get(
                "revision_count",
                0
            )

            critique = state_update.get(
                "critique",
                {}
            )

            print(
                "Revision:",
                revision_count
            )

            print(
                "Needs revision:",
                critique.get(
                    "needs_revision",
                    False
                )
            )


# ============================================================
# WORKFLOW TIMING
# ============================================================

workflow_elapsed = (
    time.perf_counter()
    - workflow_start
)


# ============================================================
# FINAL RESULT
# ============================================================

print()
print("=" * 60)
print("WORKFLOW COMPLETE")
print("=" * 60)
print()

print(
    f"Total workflow time: "
    f"{workflow_elapsed:.2f} seconds"
)

print(
    f"Session ID: {session_id}"
)

print(
    f"Revisions: "
    f"{final_state.get('revision_count', 0)}"
)

print()


# ============================================================
# GUARDRAIL RESULT
# ============================================================

guardrail_result = final_state.get(
    "guardrail_result",
    {}
)

if guardrail_result:

    print(
        "Guardrail passed:",
        guardrail_result.get(
            "passed",
            False
        )
    )

print()


# ============================================================
# FINAL ARTICLE
# ============================================================

article = final_state.get(
    "article",
    {}
)

if article:

    print("=" * 60)
    print("FINAL ARTICLE")
    print("=" * 60)
    print()

    print("TITLE")
    print("-" * 60)
    print(article.get("title", "N/A"))

    print()

    print("SUMMARY")
    print("-" * 60)
    print(article.get("summary", "N/A"))

    print()

else:

    print(
        "No final article was generated."
    )


# ============================================================
# SESSION MEMORY
# ============================================================

print()
print("=" * 60)
print("SESSION")
print("=" * 60)
print()

print(
    "Final article is available in session memory."
)

print()
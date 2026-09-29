import json

from memory.session_memory import (
    list_sessions,
    get_latest_artifact,
    save_artifact,
)

from agents.critic_agent import critique_article


# =================================================
# GET SESSION
# =================================================

sessions = list_sessions()

if not sessions:

    print("No sessions found.")
    exit()


session = sessions[0]

print("SESSION")
print("ID:", session.id)
print("TITLE:", session.title)


# =================================================
# GET ARTICLE
# =================================================

article_artifact = get_latest_artifact(
    session.id,
    "article"
)

if not article_artifact:

    print("No article found.")
    exit()


# =================================================
# GET GUARDRAIL
# =================================================

guardrail_artifact = get_latest_artifact(
    session.id,
    "guardrail"
)

if not guardrail_artifact:

    print("No guardrail result found.")
    exit()


# =================================================
# LOAD DATA
# =================================================

article = json.loads(
    article_artifact.content
)

guardrail_result = json.loads(
    guardrail_artifact.content
)


# =================================================
# RUN CRITIC
# =================================================

print()
print("Running critic agent...")
print()


critique = critique_article(

    article=article,

    guardrail_result=guardrail_result

)


# =================================================
# SAVE CRITIQUE
# =================================================

save_artifact(

    session_id=session.id,

    artifact_type="critique",

    content=json.dumps(
        critique,
        indent=2
    )

)


# =================================================
# DISPLAY
# =================================================

print()
print("========== CRITIC RESULT ==========")
print()

print(
    "NEEDS REVISION:",
    critique["needs_revision"]
)

print()

print("OVERALL FEEDBACK:")
print(
    critique["overall_feedback"]
)

print()

print("REVISION INSTRUCTIONS:")

if critique["revision_instructions"]:

    for instruction in critique["revision_instructions"]:

        print(
            f"- {instruction}"
        )

else:

    print(
        "No revision instructions."
    )

print()

print("Critique saved to session memory.")
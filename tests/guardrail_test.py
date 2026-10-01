import json

from memory.session_memory import (
    list_sessions,
    get_latest_artifact,
    save_artifact,
    update_session,
)

from agents.guardrail_agent import check_article


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
# GET TRANSCRIPT
# =================================================

transcript_artifact = get_latest_artifact(
    session.id,
    "transcript"
)

if not transcript_artifact:

    print("No transcript found.")
    exit()


# =================================================
# GET RESEARCH
# =================================================

research_artifact = get_latest_artifact(
    session.id,
    "research"
)

if not research_artifact:

    print("No research found.")
    exit()


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
# LOAD DATA
# =================================================

research = json.loads(
    research_artifact.content
)

article = json.loads(
    article_artifact.content
)


# =================================================
# RUN GUARDRAILS
# =================================================

print()
print("Running article guardrails...")
print()


guardrail_result = check_article(

    transcript=transcript_artifact.content,

    research=research,

    article=article

)


# =================================================
# SAVE RESULT
# =================================================

save_artifact(

    session_id=session.id,

    artifact_type="guardrail",

    content=json.dumps(
        guardrail_result,
        indent=2
    )

)


if guardrail_result["passed"]:

    update_session(
        session.id,
        status="guardrail_passed"
    )

else:

    update_session(
        session.id,
        status="guardrail_failed"
    )


# =================================================
# DISPLAY
# =================================================

print()
print("========== GUARDRAIL RESULT ==========")
print()

print(
    "PASSED:",
    guardrail_result["passed"]
)

print()

print(
    "SUMMARY:"
)

print(
    guardrail_result["summary"]
)

print()

print(
    "VIOLATIONS:",
    len(guardrail_result["violations"])
)

print()

for violation in guardrail_result["violations"]:

    print("TYPE:")
    print(violation["type"])

    print("SEVERITY:")
    print(violation["severity"])

    print("ARTICLE TEXT:")
    print(violation["article_text"])

    print("EXPLANATION:")
    print(violation["explanation"])

    print("-" * 60)

print()
print("Guardrail result saved to session memory.")
import json

from memory.session_memory import (
    list_sessions,
    get_latest_artifact,
    save_artifact,
    update_session,
)

from agents.writer_agent import write_article
from agents.guardrail_agent import check_article
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
# LOAD TRANSCRIPT
# =================================================

transcript_artifact = get_latest_artifact(
    session.id,
    "transcript"
)

if not transcript_artifact:
    print("No transcript found.")
    exit()


# =================================================
# LOAD ANALYSIS
# =================================================

analysis_artifact = get_latest_artifact(
    session.id,
    "analysis"
)

if not analysis_artifact:
    print("No analysis found.")
    exit()


# =================================================
# LOAD RESEARCH
# =================================================

research_artifact = get_latest_artifact(
    session.id,
    "research"
)

if not research_artifact:
    print("No research found.")
    exit()


# =================================================
# LOAD CONTENT
# =================================================

transcript = transcript_artifact.content

analysis = json.loads(
    analysis_artifact.content
)

research = json.loads(
    research_artifact.content
)


# =================================================
# INITIAL WRITER
# =================================================

print()
print("Generating initial article...")
print()

article = write_article(
    transcript=transcript,
    analysis=analysis,
    research=research
)


# =================================================
# REVISION LOOP
# =================================================

MAX_REVISIONS = 2

for revision_number in range(MAX_REVISIONS + 1):

    print()
    print("=" * 60)
    print(
        f"GUARDRAIL CHECK — ATTEMPT {revision_number + 1}"
    )
    print("=" * 60)
    print()


    # =============================================
    # GUARDRAIL
    # =============================================

    guardrail_result = check_article(
        transcript=transcript,
        research=research,
        article=article
    )


    # =============================================
    # SAVE GUARDRAIL RESULT
    # =============================================

    save_artifact(
        session_id=session.id,
        artifact_type="guardrail",
        content=json.dumps(
            guardrail_result,
            indent=2
        )
    )


    print(
        "PASSED:",
        guardrail_result["passed"]
    )

    print(
        "VIOLATIONS:",
        len(guardrail_result["violations"])
    )


    # =============================================
    # IF GUARDRAIL PASSES
    # =============================================

    if guardrail_result["passed"]:

        print()
        print("✅ ARTICLE PASSED GUARDRAILS")
        print()

        update_session(
            session.id,
            status="article_ready"
        )

        break


    # =============================================
    # MAXIMUM REVISION CHECK
    # =============================================

    if revision_number == MAX_REVISIONS:

        print()
        print("❌ MAXIMUM REVISIONS REACHED")
        print()

        update_session(
            session.id,
            status="guardrail_failed"
        )

        break


    # =============================================
    # CRITIC
    # =============================================

    print()
    print("Running critic...")
    print()

    critique = critique_article(
        article=article,
        guardrail_result=guardrail_result
    )


    # =============================================
    # SAVE CRITIQUE
    # =============================================

    save_artifact(
        session_id=session.id,
        artifact_type="critique",
        content=json.dumps(
            critique,
            indent=2
        )
    )


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

        for instruction in critique[
            "revision_instructions"
        ]:

            print(
                f"- {instruction}"
            )

    else:

        print(
            "No revision instructions."
        )


    # =============================================
    # CRITIC SAYS NO REVISION
    # =============================================

    if not critique["needs_revision"]:

        print()
        print(
            "Critic does not require revision."
        )

        update_session(
            session.id,
            status="article_ready"
        )

        break


    # =============================================
    # SEND CRITIQUE BACK TO WRITER
    # =============================================

    print()
    print("Sending critique back to Writer...")
    print()

    article = write_article(
        transcript=transcript,
        analysis=analysis,
        research=research,
        critique=critique
    )


# =================================================
# SAVE FINAL ARTICLE
# =================================================

save_artifact(
    session_id=session.id,
    artifact_type="article",
    content=json.dumps(
        article,
        indent=2
    )
)


# =================================================
# DISPLAY FINAL ARTICLE
# =================================================

print()
print("=" * 60)
print("FINAL ARTICLE")
print("=" * 60)
print()

print("TITLE:")
print(article["title"])

print()

print("SUMMARY:")
print(article["summary"])

print()

print("ARTICLE:")
print(article["article"])

print()

print("Final article saved to session memory.")
import json

from memory.session_memory import (
    list_sessions,
    get_latest_artifact,
    save_artifact,
    update_session,
)

from agents.writer_agent import write_article


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
# GET ANALYSIS
# =================================================

analysis_artifact = get_latest_artifact(
    session.id,
    "analysis"
)

if not analysis_artifact:

    print("No analysis found.")
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
# LOAD DATA
# =================================================

analysis = json.loads(
    analysis_artifact.content
)

research = json.loads(
    research_artifact.content
)


# =================================================
# WRITE ARTICLE
# =================================================

print()
print("Writing article with GPT-5.4...")
print()


article = write_article(

    transcript=transcript_artifact.content,

    analysis=analysis,

    research=research

)


# =================================================
# SAVE ARTICLE
# =================================================

save_artifact(

    session_id=session.id,

    artifact_type="article",

    content=json.dumps(
        article,
        indent=2
    )

)


update_session(

    session.id,

    status="article_ready"

)


# =================================================
# DISPLAY
# =================================================

print()
print("========== ARTICLE COMPLETE ==========")
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
print("Article saved to session memory.")
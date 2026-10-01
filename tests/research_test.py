import json

from memory.session_memory import (
    list_sessions,
    get_latest_artifact,
    save_artifact,
    update_session,
)

from agents.research_agent import research_claims


sessions = list_sessions()

if not sessions:
    print("No sessions found.")
    exit()


session = sessions[0]

print("SESSION")
print("ID:", session.id)
print("TITLE:", session.title)


analysis_artifact = get_latest_artifact(
    session.id,
    "analysis"
)

if not analysis_artifact:

    print("No analysis found.")
    exit()


analysis = json.loads(
    analysis_artifact.content
)


print()
print("Researching verification-required claims...")
print()


research_results = research_claims(
    analysis["claims"]
)

save_artifact(
    session_id=session.id,
    artifact_type="research",
    content=json.dumps(
        research_results,
        indent=2
    )
)

update_session(
    session.id,
    status="research_ready"
)

print()
print("Research saved to session memory.")



import json

from memory.session_memory import (
    list_sessions,
    get_latest_artifact,
    save_artifact,
    update_session,
)

from agents.analysis_agent import analyze_transcript


# Get latest session
sessions = list_sessions()

if not sessions:
    print("No sessions found.")
    exit()

session = sessions[0]

print("SESSION")
print("ID:", session.id)
print("TITLE:", session.title)


# Retrieve transcript from session memory
transcript_artifact = get_latest_artifact(
    session.id,
    "transcript"
)

if not transcript_artifact:
    print("\nNo transcript found.")
    exit()


print("\nTranscript retrieved successfully.")

print("\nRunning Analysis Agent...")
print("Sending transcript to GPT-5.4...")

analysis = analyze_transcript(
    transcript_artifact.content
)

save_artifact(
    session_id=session.id,
    artifact_type="analysis",
    content=json.dumps(analysis, indent=2)
)

update_session(
    session.id,
    status="analysis_ready"
)

print("\nAnalysis saved to session memory.")

print("\n========== ANALYSIS RESULT ==========\n")

print("SPEAKERS:")
print(analysis["speakers"])

print("\nTOPICS:")
print(analysis["topics"])

print("\nCLAIMS:")
for claim in analysis["claims"]:
    print(claim)

print("\nQUOTES:")
for quote in analysis["quotes"]:
    print(quote)

print("\nAGREEMENTS:")
print(analysis["agreements"])

print("\nDISAGREEMENTS:")
print(analysis["disagreements"])
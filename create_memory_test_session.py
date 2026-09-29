from memory.session_memory import (
    create_session,
    save_artifact,
)

from agents.transcript_agent import get_transcript
from agents.analysis_agent import analyze_transcript


# --------------------------------------------------
# CREATE TEMPORARY SESSION
# --------------------------------------------------

podcast_url = "https://youtu.be/l9AzO1FMgM8?si=WUIBimKcuoU65Tx-"

session = create_session(
    title="Semantic Memory Test",
    podcast_url=podcast_url,
)

print("=" * 60)
print("CREATED TEST SESSION")
print("=" * 60)

print("Session ID:", session.id)


# --------------------------------------------------
# TRANSCRIPT
# --------------------------------------------------

print("\n🎙️ Getting transcript...")

transcript = get_transcript(podcast_url)

save_artifact(
    session_id=session.id,
    artifact_type="transcript",
    content=transcript,
)

print("✓ Transcript saved")


# --------------------------------------------------
# ANALYSIS
# --------------------------------------------------

print("\n🧠 Analyzing transcript...")

analysis = analyze_transcript(transcript)

import json

save_artifact(
    session_id=session.id,
    artifact_type="analysis",
    content=json.dumps(analysis),
)

print("✓ Analysis saved")


print("\n" + "=" * 60)
print("PARTIAL SESSION CREATED")
print("=" * 60)

print("Session ID:", session.id)
print("Saved artifacts:")
print("  ✓ transcript")
print("  ✓ analysis")
print("  ✗ research")
print("  ✗ article")
print("  ✗ guardrail")
print("=" * 60)
from backend.agents.transcript_agent import get_transcript
from backend.utils.chunking import chunk_transcript
from backend.agents.chunk_summary_agent import summarize_chunk
from backend.agents.analysis_agent import analyze_transcript


url = "https://youtu.be/l9AzO1FMgM8?si=WUIBimKcuoU65Tx-"

# 1. Get transcript
transcript = get_transcript(url)

# 2. Chunk transcript
chunks = chunk_transcript(
    transcript,
    chunk_duration=300
)

# 3. Summarize chunks
chunk_summaries = []

for chunk in chunks:
    summary = summarize_chunk(chunk)
    chunk_summaries.append(summary)

# 4. Analyze using summaries + raw transcript
analysis = analyze_transcript(
    transcript=transcript,
    chunk_summaries=chunk_summaries
)

print("\n" + "=" * 70)
print("ANALYSIS RESULT")
print("=" * 70)

print("\nSPEAKERS:")
print(analysis["speakers"])

print("\nTOPICS:")
for topic in analysis["topics"]:
    print("-", topic)

print("\nCLAIMS:")
print("\nCLAIMS:")

for claim in analysis["claims"]:
    print(
        f"[{claim['timestamp']}] {claim['claim']}\n"
        f"  Type: {claim['claim_type']}\n"
        f"  Priority: {claim['priority']}\n"
        f"  Verify: {claim['requires_verification']}\n"
    )

print("\nQUOTES:")
for quote in analysis["quotes"]:
    print(
        f"[{quote['timestamp']}] "
        f"{quote['quote']}"
    )

print("\nAGREEMENTS:")
for item in analysis["agreements"]:
    print("-", item)

print("\nDISAGREEMENTS:")
for item in analysis["disagreements"]:
    print("-", item)
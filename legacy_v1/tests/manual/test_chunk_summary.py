from backend.agents.transcript_agent import get_transcript
from backend.utils.chunking import chunk_transcript
from backend.agents.chunk_summary_agent import summarize_chunk


url = "https://youtu.be/l9AzO1FMgM8?si=WUIBimKcuoU65Tx-"


# 1. Get transcript
transcript = get_transcript(url)


# 2. Chunk transcript
chunks = chunk_transcript(
    transcript,
    chunk_duration=300
)


print(f"Transcript length: {len(transcript)}")
print(f"Number of chunks: {len(chunks)}")


# 3. Summarize each chunk
for chunk in chunks:

    print()
    print("=" * 70)
    print(
        f"CHUNK {chunk['chunk_id']} | "
        f"{chunk['start_timestamp']} - "
        f"{chunk['end_timestamp']}"
    )
    print("=" * 70)

    summary = summarize_chunk(chunk)

    print("\nSUMMARY:")
    print(summary["summary"])

    print("\nKEY POINTS:")

    for point in summary["key_points"]:
        print(
            f"[{point['timestamp']}] "
            f"{point['point']}"
        )
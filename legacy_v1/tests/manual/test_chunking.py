from backend.agents.transcript_agent import get_transcript
from backend.utils.chunking import chunk_transcript


url = "https://youtu.be/l9AzO1FMgM8?si=WUIBimKcuoU65Tx-"

transcript = get_transcript(url)

chunks = chunk_transcript(
    transcript,
    chunk_duration=300
)

print(f"Transcript length: {len(transcript)}")
print(f"Number of chunks: {len(chunks)}")

for chunk in chunks:

    print()
    print("=" * 60)
    print(
        f"Chunk {chunk['chunk_id']} | "
        f"{chunk['start_timestamp']} - "
        f"{chunk['end_timestamp']}"
    )
    print("=" * 60)

    print(f"Segments: {len(chunk['segments'])}")

    for segment in chunk["segments"]:
        print(
            f"[{segment['timestamp']}] "
            f"{segment['text']}"
        )
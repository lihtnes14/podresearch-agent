import re


def chunk_transcript(
    transcript: str,
    chunk_duration: int = 300,
) -> list[dict]:

    lines = transcript.splitlines()

    chunks = {}

    timestamp_pattern = re.compile(
        r"\[(\d+):(\d{2})\]\s*(.*)"
    )

    for line in lines:

        match = timestamp_pattern.match(line)

        if not match:
            continue

        minutes = int(match.group(1))
        seconds = int(match.group(2))
        text = match.group(3).strip()

        timestamp_seconds = minutes * 60 + seconds

        chunk_id = timestamp_seconds // chunk_duration

        if chunk_id not in chunks:
            chunks[chunk_id] = []

        chunks[chunk_id].append(
            {
                "timestamp": format_timestamp(timestamp_seconds),
                "text": text,
            }
        )

    result = []

    for chunk_id in sorted(chunks):

        start_seconds = chunk_id * chunk_duration
        end_seconds = (chunk_id + 1) * chunk_duration

        segments = chunks[chunk_id]

        result.append(
            {
                "chunk_id": chunk_id + 1,
                "start_timestamp": format_timestamp(
                    start_seconds
                ),
                "end_timestamp": format_timestamp(
                    end_seconds
                ),
                "segments": segments,
            }
        )

    return result


def format_timestamp(seconds: int) -> str:

    minutes = seconds // 60
    remaining_seconds = seconds % 60

    return f"{minutes:02d}:{remaining_seconds:02d}"
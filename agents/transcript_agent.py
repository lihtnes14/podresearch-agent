from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs


def extract_video_id(url: str) -> str:
    parsed_url = urlparse(url)

    # youtube.com/watch?v=VIDEO_ID
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        return parse_qs(parsed_url.query)["v"][0]

    # youtu.be/VIDEO_ID
    if parsed_url.hostname == "youtu.be":
        return parsed_url.path.strip("/")

    raise ValueError("Invalid YouTube URL")


def get_transcript(url: str) -> str:
    video_id = extract_video_id(url)

    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id)

    text = []

    for entry in transcript:
        timestamp = int(entry.start)

        minutes = timestamp // 60
        seconds = timestamp % 60

        formatted_time = f"{minutes:02d}:{seconds:02d}"

        text.append(
            f"[{formatted_time}] {entry.text}"
        )

    return "\n".join(text)
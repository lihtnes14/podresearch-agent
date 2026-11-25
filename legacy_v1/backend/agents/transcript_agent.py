import time

from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs


def extract_video_id(url: str) -> str:
    parsed_url = urlparse(url)

    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        return parse_qs(parsed_url.query)["v"][0]

    if parsed_url.hostname == "youtu.be":
        return parsed_url.path.strip("/")

    raise ValueError("Invalid YouTube URL")


def get_transcript(url: str, retries: int = 3) -> str:
    video_id = extract_video_id(url)

    api = YouTubeTranscriptApi()

    last_error = None

    for attempt in range(retries):
        try:
            transcript = api.fetch(video_id)
            break

        except Exception as e:
            last_error = e

            print(
                f"Transcript fetch failed "
                f"(attempt {attempt + 1}/{retries}): {e}"
            )

            if attempt < retries - 1:
                time.sleep(2 ** attempt)

    else:
        raise RuntimeError(
            f"Could not retrieve transcript for YouTube video "
            f"{video_id} after {retries} attempts."
        ) from last_error

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
import time
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str:
    """Extract video ID from standard or shortened YouTube URLs."""
    parsed_url = urlparse(url)

    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        query_params = parse_qs(parsed_url.query)
        if "v" in query_params:
            return query_params["v"][0]

    if parsed_url.hostname == "youtu.be":
        return parsed_url.path.strip("/")

    raise ValueError(f"Invalid YouTube URL: {url}")


def get_transcript(url: str, retries: int = 3) -> str:
    """Fetch transcript from YouTube and format with timestamps [MM:SS]."""
    video_id = extract_video_id(url)
    api = YouTubeTranscriptApi()
    last_error = None

    for attempt in range(retries):
        try:
            if hasattr(api, "fetch"):
                transcript = api.fetch(video_id)
            else:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
            break
        except Exception as e:
            last_error = e
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    else:
        raise RuntimeError(
            f"Could not retrieve transcript for YouTube video {video_id} after {retries} attempts."
        ) from last_error

    text = []
    for entry in transcript:
        start_time = getattr(entry, "start", None) if hasattr(entry, "start") else entry.get("start", 0)
        content = getattr(entry, "text", None) if hasattr(entry, "text") else entry.get("text", "")
        
        timestamp = int(start_time)
        minutes = timestamp // 60
        seconds = timestamp % 60
        formatted_time = f"{minutes:02d}:{seconds:02d}"
        text.append(f"[{formatted_time}] {content}")

    return "\n".join(text)

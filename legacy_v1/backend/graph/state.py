from typing import TypedDict


class PodcastState(TypedDict):
    session_id: str
    podcast_url: str
    transcript: str
    analysis: dict
    historical_context: list[dict]
    research: list[dict]
    article: dict
    guardrail_result: dict
    critique: dict
    revision_count: int
    loaded_artifacts: list[str]
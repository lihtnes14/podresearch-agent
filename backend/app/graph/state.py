from typing import TypedDict, Optional, List, Dict, Any


class PodcastArticleState(TypedDict, total=False):
    session_id: str
    podcast_url: str
    video_title: str
    video_description: Optional[str]
    article_style: str
    target_audience: Optional[str]

    # Ingestion & Segmenting
    transcript: str
    chunks: List[Dict[str, Any]]

    # Multi-Agent Outputs
    outline: Optional[Dict[str, Any]]
    article: Optional[Dict[str, Any]]
    review: Optional[Dict[str, Any]]

    # Human-in-the-Loop & Revisions
    human_decisions: Optional[List[Dict[str, Any]]]
    human_instructions: Optional[str]
    revision_count: int
    final_article: Optional[str]
    status: str
    error: Optional[str]

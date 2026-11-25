from typing import Optional, Dict, Any, List
from langgraph.graph import StateGraph, START, END
from app.graph.state import PodcastArticleState
from app.utils.transcript import get_transcript
from app.utils.chunking import chunk_transcript
from app.agents.content_analyst import generate_article_outline
from app.agents.article_writer import write_article
from app.agents.editorial_reviewer import review_article
from app.schemas import ArticleOutline, ArticleOutput
from app.storage.session_store import get_session_store


def extract_and_chunk_node(state: PodcastArticleState) -> dict:
    """Node 1: Extract subtitles from YouTube and partition into time-based chunks."""
    podcast_url = state["podcast_url"]
    transcript = get_transcript(podcast_url)
    chunks = chunk_transcript(transcript, chunk_duration=300)

    store = get_session_store()
    store.save_session(
        session_id=state["session_id"],
        podcast_url=podcast_url,
        status="chunks_extracted",
        transcript=transcript,
        chunks=chunks,
    )

    return {
        "transcript": transcript,
        "chunks": chunks,
        "status": "chunks_extracted",
    }


def content_analyst_node(state: PodcastArticleState) -> dict:
    """Node 2 (Agent 1): Generate structured article outline from transcript chunks."""
    chunks = state["chunks"]
    outline = generate_article_outline(chunks)

    store = get_session_store()
    store.save_session(
        session_id=state["session_id"],
        podcast_url=state["podcast_url"],
        status="outline_generated",
        outline=outline.model_dump(),
    )

    return {
        "outline": outline.model_dump(),
        "status": "outline_generated",
    }


def article_writer_node(state: PodcastArticleState) -> dict:
    """Node 3 (Agent 2): Write full Markdown article from transcript and outline."""
    chunks = state["chunks"]
    outline = ArticleOutline.model_validate(state["outline"])
    video_title = state.get("video_title") or outline.article_title

    article = write_article(
        video_title=video_title,
        chunks=chunks,
        outline=outline,
        video_url=state["podcast_url"],
        article_style=state.get("article_style", "technical, clear, and authoritative"),
        target_audience=state.get("target_audience"),
        video_description=state.get("video_description", ""),
    )

    store = get_session_store()
    session = store.get_session(state["session_id"]) or {}
    history = session.get("history", [])
    history.append({
        "version": len(history) + 1,
        "article": article.model_dump(),
        "type": "draft",
    })

    store.save_session(
        session_id=state["session_id"],
        podcast_url=state["podcast_url"],
        video_title=video_title,
        status="article_drafted",
        article=article.model_dump(),
        history=history,
    )

    return {
        "video_title": video_title,
        "article": article.model_dump(),
        "status": "article_drafted",
    }


def editorial_reviewer_node(state: PodcastArticleState) -> dict:
    """Node 4 (Agent 3): Audit article quality, grounding, timestamps, and uncertainties."""
    chunks = state["chunks"]
    outline = ArticleOutline.model_validate(state["outline"])
    article = ArticleOutput.model_validate(state["article"])

    review = review_article(chunks=chunks, outline=outline, article=article)

    status = "awaiting_human_review"
    store = get_session_store()
    store.save_session(
        session_id=state["session_id"],
        podcast_url=state["podcast_url"],
        status=status,
        review=review.model_dump(),
    )

    return {
        "review": review.model_dump(),
        "status": status,
    }


def create_article_workflow():
    """Builds and compiles the multi-agent LangGraph workflow."""
    builder = StateGraph(PodcastArticleState)

    builder.add_node("extract_and_chunk", extract_and_chunk_node)
    builder.add_node("content_analyst", content_analyst_node)
    builder.add_node("article_writer", article_writer_node)
    builder.add_node("editorial_reviewer", editorial_reviewer_node)

    # Linear autonomous execution up to Human Review
    builder.add_edge(START, "extract_and_chunk")
    builder.add_edge("extract_and_chunk", "content_analyst")
    builder.add_edge("content_analyst", "article_writer")
    builder.add_edge("article_writer", "editorial_reviewer")
    builder.add_edge("editorial_reviewer", END)

    return builder.compile()


workflow = create_article_workflow()


def run_article_pipeline(
    session_id: str,
    podcast_url: str,
    video_title: Optional[str] = None,
    video_description: Optional[str] = None,
    article_style: str = "technical, clear, and authoritative",
    target_audience: Optional[str] = None,
) -> dict:
    """Runs the article generation pipeline through LangGraph."""
    initial_state: PodcastArticleState = {
        "session_id": session_id,
        "podcast_url": podcast_url,
        "video_title": video_title or "",
        "video_description": video_description or "",
        "article_style": article_style,
        "target_audience": target_audience,
        "revision_count": 0,
        "status": "started",
    }

    final_state = workflow.invoke(initial_state)
    return final_state

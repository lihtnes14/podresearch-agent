import uuid
import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.schemas import (
    GenerateArticleRequest,
    HumanReviewRequest,
    HumanApproveRequest,
    PublishMediumRequest,
    PublishMediumResponse,
    PublishDevtoRequest,
    PublishDevtoResponse,
    HealthResponse,
    ArticleOutline,
    ArticleOutput,
)
from app.config import settings
from app.services.medium_service import publish_article_to_medium, MediumServiceError
from app.services.devto_service import publish_article_to_devto, DevtoServiceError
from app.storage.session_store import get_session_store
from app.graph.workflow import workflow
from app.agents.article_writer import revise_article
from app.agents.editorial_reviewer import review_article

router = APIRouter(prefix="/api", tags=["YouTube Article Generator API"])


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    return HealthResponse()


@router.post("/sessions/generate", status_code=status.HTTP_201_CREATED)
def generate_article(request: GenerateArticleRequest):
    """
    Kicks off the end-to-end multi-agent pipeline:
    Extraction -> Agent 1 (Analyst) -> Agent 2 (Writer) -> Agent 3 (Reviewer)
    Pauses at the Human Review Stage.
    """
    session_id = str(uuid.uuid4())
    store = get_session_store()
    store.save_session(
        session_id=session_id,
        podcast_url=request.podcast_url,
        video_title=request.video_title,
        video_description=request.video_description,
        status="processing",
    )

    try:
        initial_state = {
            "session_id": session_id,
            "podcast_url": request.podcast_url,
            "video_title": request.video_title or "",
            "video_description": request.video_description or "",
            "article_style": request.article_style or "technical, clear, and authoritative",
            "target_audience": request.target_audience,
            "revision_count": 0,
            "status": "processing",
        }

        final_state = workflow.invoke(initial_state)
        session = store.get_session(session_id)
        return {
            "session_id": session_id,
            "status": session["status"],
            "title": session["video_title"],
            "article": session["article"],
            "review": session["review"],
            "outline": session["outline"],
        }
    except Exception as e:
        store.save_session(
            session_id=session_id,
            podcast_url=request.podcast_url,
            status="failed",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline generation failed: {str(e)}",
        )


@router.get("/sessions")
def list_sessions():
    """Returns a list of all generation sessions."""
    store = get_session_store()
    return store.list_sessions()


@router.get("/sessions/{session_id}")
def get_session_details(session_id: str):
    """Retrieves full details, artifacts, and version history for a session."""
    store = get_session_store()
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )
    return session


@router.post("/sessions/{session_id}/human-review")
def submit_human_review(session_id: str, payload: HumanReviewRequest):
    """
    Saves human editor decisions (accepted/rejected suggestions, direct edits).
    """
    store = get_session_store()
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    # If direct markdown edits were provided, update article draft
    if payload.direct_markdown_edits:
        current_article = session.get("article") or {}
        current_article["markdown_article"] = payload.direct_markdown_edits
        history = session.get("history", [])
        history.append({
            "version": len(history) + 1,
            "article": current_article,
            "action": "Direct Human Edit",
        })
        store.save_session(
            session_id=session_id,
            podcast_url=session["podcast_url"],
            status="human_edited",
            article=current_article,
            history=history,
        )

    return {
        "session_id": session_id,
        "message": "Human review decisions saved successfully.",
        "status": store.get_session(session_id)["status"],
    }


@router.post("/sessions/{session_id}/revise")
def trigger_agent_revision(session_id: str, payload: HumanReviewRequest):
    """
    Triggers Agent 2 to revise the draft based on human accepted suggestions,
    then automatically re-runs Agent 3 to audit the revised article.
    """
    store = get_session_store()
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    chunks = session.get("chunks", [])
    outline = ArticleOutline.model_validate(session["outline"])
    current_article = session.get("article", {})
    previous_markdown = current_article.get("markdown_article", "")

    # Collect accepted issues
    review_issues = (session.get("review") or {}).get("issues", [])
    accepted_feedback = []
    for item in payload.decisions:
        if item.decision.lower() == "accept" and 0 <= item.issue_index < len(review_issues):
            issue_obj = review_issues[item.issue_index]
            feedback_str = f"Section '{issue_obj.get('section')}': {issue_obj.get('issue')}"
            if item.notes:
                feedback_str += f" (Note: {item.notes})"
            accepted_feedback.append(feedback_str)

    if payload.selected_feedback:
        for item in payload.selected_feedback:
            if isinstance(item, dict):
                sec = item.get("section", "General")
                iss = item.get("issue", "")
                inst = item.get("custom_instruction")
                fb = f"Section '{sec}': {iss}"
                if inst:
                    fb += f" (Note: {inst})"
                accepted_feedback.append(fb)
            elif isinstance(item, str):
                accepted_feedback.append(item)

    direct_edits = payload.direct_markdown_edits or payload.direct_article_edits
    if direct_edits:
        previous_markdown = direct_edits

    instructions = payload.custom_instructions or payload.additional_instructions or ""

    try:
        # 1. Agent 2 Revision
        revised = revise_article(
            previous_article_markdown=previous_markdown,
            human_instructions=instructions,
            accepted_feedback=accepted_feedback,
            chunks=chunks,
            outline=outline,
        )

        # 2. Agent 3 Re-audit
        new_review = review_article(chunks=chunks, outline=outline, article=revised)

        # 3. Store new version
        history = session.get("history", [])
        history.append({
            "version": len(history) + 1,
            "article": revised.model_dump(),
            "review": new_review.model_dump(),
            "action": "Agent 2 Revision",
        })

        store.save_session(
            session_id=session_id,
            podcast_url=session["podcast_url"],
            status="revised",
            article=revised.model_dump(),
            review=new_review.model_dump(),
            history=history,
        )

        return {
            "session_id": session_id,
            "status": "revised",
            "article": revised.model_dump(),
            "review": new_review.model_dump(),
            "version": len(history),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Revision failed: {str(e)}",
        )


@router.post("/sessions/{session_id}/approve")
def approve_article(session_id: str, payload: HumanApproveRequest):
    """
    Issues official Human Editorial Approval.
    Locks the final article for publication and returns the publication payload.
    """
    store = get_session_store()
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    current_article = session.get("article", {})
    final_markdown = (
        payload.final_article
        or current_article.get("markdown_article")
        or current_article.get("content", "")
    )
    notes = payload.editor_notes or payload.reviewer_notes or "Approved by Human Editor-in-Chief."

    store.save_session(
        session_id=session_id,
        podcast_url=session["podcast_url"],
        status="approved",
        final_article=final_markdown,
    )

    return {
        "session_id": session_id,
        "status": "approved",
        "title": current_article.get("title", session.get("video_title")),
        "final_article": final_markdown,
        "editor_notes": notes,
        "message": "🏆 Article officially approved and ready for publication!",
    }


@router.post("/sessions/{session_id}/publish/medium", response_model=PublishMediumResponse)
def publish_to_medium(session_id: str, payload: PublishMediumRequest):
    """
    Publishes the approved article directly to the user's Medium account.
    Creates a draft or published story using Medium's REST API.
    """
    store = get_session_store()
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    # Resolve Medium Token
    token = (payload.medium_token or "").strip() or settings.MEDIUM_INTEGRATION_TOKEN
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medium Integration Token is required. Please provide it in the publish dialog or set MEDIUM_INTEGRATION_TOKEN in your .env file.",
        )

    # Resolve Article Content
    article_content = (
        session.get("final_article")
        or (session.get("article") or {}).get("markdown_article")
        or (session.get("article") or {}).get("content")
    )
    if not article_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No article content found to publish. Please generate and approve an article first.",
        )

    title = (
        (session.get("article") or {}).get("title")
        or session.get("video_title")
        or "Generated YouTube Article"
    )
    canonical_url = payload.canonical_url or session.get("podcast_url")

    try:
        result = publish_article_to_medium(
            token=token,
            title=title,
            markdown_content=article_content,
            tags=payload.tags,
            publish_status=payload.publish_status,
            canonical_url=canonical_url,
        )

        # Update session store with Medium publication record
        store.save_session(
            session_id=session_id,
            podcast_url=session["podcast_url"],
            status="published_to_medium",
            final_article=article_content,
        )

        return PublishMediumResponse(
            success=True,
            post_url=result["post_url"],
            post_id=result["post_id"],
            publish_status=result["publish_status"],
            title=result["title"],
            author_name=result["author_name"],
            author_url=result.get("author_url"),
            message=f"🎉 Successfully published to Medium as a {result['publish_status']}!",
        )
    except MediumServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error publishing to Medium: {str(e)}",
        )


@router.post("/sessions/{session_id}/publish/devto", response_model=PublishDevtoResponse)
def publish_to_devto(session_id: str, payload: PublishDevtoRequest):
    """
    Publishes the approved article automatically to the user's Dev.to blog.
    Supports draft or instant live publication using the Dev.to REST API.
    """
    store = get_session_store()
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    # Resolve Dev.to API Key
    api_key = (payload.api_key or "").strip() or settings.DEVTO_API_KEY
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dev.to API Key is required. Generate one free in 5 seconds at https://dev.to/settings/extensions.",
        )

    # Resolve Article Content
    article_content = (
        session.get("final_article")
        or (session.get("article") or {}).get("markdown_article")
        or (session.get("article") or {}).get("content")
    )
    if not article_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No article content found to publish. Please generate and approve an article first.",
        )

    title = (
        (session.get("article") or {}).get("title")
        or session.get("video_title")
        or "Generated YouTube Article"
    )
    canonical_url = payload.canonical_url or session.get("podcast_url")

    try:
        result = publish_article_to_devto(
            api_key=api_key,
            title=title,
            markdown_content=article_content,
            tags=payload.tags,
            published=payload.published,
            canonical_url=canonical_url,
        )

        # Update session store
        store.save_session(
            session_id=session_id,
            podcast_url=session["podcast_url"],
            status="published_to_devto",
            final_article=article_content,
        )

        status_str = "live article" if result["published"] else "draft"
        return PublishDevtoResponse(
            success=True,
            post_url=result["post_url"],
            post_id=result["post_id"],
            published=result["published"],
            title=result["title"],
            author_name=result["author_name"],
            author_username=result.get("author_username"),
            message=f"🚀 Successfully automated post to Dev.to as a {status_str}!",
        )
    except DevtoServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error publishing to Dev.to: {str(e)}",
        )


@router.get("/sessions/{session_id}/stream")
def stream_article_generation(session_id: str):
    """Streams live LangGraph node execution events using Server-Sent Events (SSE)."""
    store = get_session_store()
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    initial_state = {
        "session_id": session_id,
        "podcast_url": session["podcast_url"],
        "video_title": session.get("video_title") or "",
        "video_description": session.get("video_description") or "",
        "article_style": "technical, clear, and authoritative",
        "revision_count": 0,
        "status": "streaming",
    }

    def event_generator():
        yield f"event: start\ndata: {json.dumps({'session_id': session_id, 'status': 'started'})}\n\n"
        for event in workflow.stream(initial_state):
            for node_name, update in event.items():
                event_data = {
                    "session_id": session_id,
                    "node": node_name,
                    "status": update.get("status"),
                }
                yield f"event: node_update\ndata: {json.dumps(event_data, default=str)}\n\n"
        yield f"event: complete\ndata: {json.dumps({'session_id': session_id, 'status': 'awaiting_human_review'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

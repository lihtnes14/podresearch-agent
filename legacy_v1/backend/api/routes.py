import json
import asyncio
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from backend.graph.workflow import workflow
from backend.memory.session_memory import (
    create_session,
    list_sessions,
    get_session,
    update_session,
    delete_session,
    get_artifacts,
    get_latest_artifact,
)
from backend.api.schemas import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    ArtifactResponse,
    SessionDetailResponse,
    RunWorkflowRequest,
    RunWorkflowResponse,
)

router = APIRouter(prefix="/api", tags=["PodResearch API"])


# =========================================================
# SESSIONS
# =========================================================

@router.post(
    "/sessions",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new research session",
)
def api_create_session(payload: SessionCreate):
    session = create_session(
        title=payload.title,
        podcast_url=payload.podcast_url,
    )
    return session


@router.get(
    "/sessions",
    response_model=List[SessionResponse],
    summary="List all research sessions",
)
def api_list_sessions():
    return list_sessions()


@router.get(
    "/sessions/{session_id}",
    response_model=SessionDetailResponse,
    summary="Get session details and all associated artifacts",
)
def api_get_session(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    artifacts = get_artifacts(session_id)
    artifact_responses = [
        ArtifactResponse.from_orm_with_parsed_data(a) for a in artifacts
    ]

    return SessionDetailResponse(
        session=SessionResponse.model_validate(session),
        artifacts=artifact_responses,
    )


@router.patch(
    "/sessions/{session_id}",
    response_model=SessionResponse,
    summary="Update session title or status",
)
def api_update_session(session_id: str, payload: SessionUpdate):
    session = update_session(
        session_id=session_id,
        title=payload.title,
        status=payload.status,
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )
    return session


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a session and its artifacts",
)
def api_delete_session(session_id: str):
    deleted = delete_session(session_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )
    return None


# =========================================================
# ARTIFACTS
# =========================================================

@router.get(
    "/sessions/{session_id}/artifacts",
    response_model=List[ArtifactResponse],
    summary="Get all artifacts for a session",
)
def api_get_artifacts(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    artifacts = get_artifacts(session_id)
    return [ArtifactResponse.from_orm_with_parsed_data(a) for a in artifacts]


@router.get(
    "/sessions/{session_id}/artifacts/{artifact_type}",
    response_model=ArtifactResponse,
    summary="Get latest artifact of a specific type (e.g. article, analysis, guardrail)",
)
def api_get_latest_artifact(session_id: str, artifact_type: str):
    artifact = get_latest_artifact(session_id, artifact_type)
    if not artifact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No artifact of type '{artifact_type}' found for session '{session_id}'.",
        )

    return ArtifactResponse.from_orm_with_parsed_data(artifact)


# =========================================================
# WORKFLOW EXECUTION
# =========================================================

def _prepare_initial_state(session) -> dict:
    return {
        "session_id": session.id,
        "podcast_url": session.podcast_url,
        "transcript": "",
        "analysis": {},
        "historical_context": [],
        "research": [],
        "article": {},
        "guardrail_result": {},
        "critique": {},
        "revision_count": 0,
        "loaded_artifacts": [],
    }


@router.post(
    "/sessions/{session_id}/run",
    response_model=RunWorkflowResponse,
    summary="Execute the research workflow synchronously",
)
def api_run_workflow(session_id: str, payload: Optional[RunWorkflowRequest] = None):
    session = get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    initial_state = _prepare_initial_state(session)

    try:
        final_state = initial_state.copy()
        for event in workflow.stream(initial_state):
            for _, state_update in event.items():
                final_state.update(state_update)

        refreshed_session = get_session(session_id)
        current_status = refreshed_session.status if refreshed_session else "completed"

        return RunWorkflowResponse(
            session_id=session_id,
            status=current_status,
            message="Workflow completed successfully.",
            final_state=final_state,
        )

    except Exception as e:
        update_session(session_id, status="failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(e)}",
        )


@router.get(
    "/sessions/{session_id}/stream",
    summary="Execute and stream workflow events in real time via Server-Sent Events (SSE)",
)
def api_stream_workflow(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    initial_state = _prepare_initial_state(session)

    def event_generator():
        # Start event
        yield (
            f"event: start\n"
            f"data: {json.dumps({'event_type': 'start', 'session_id': session_id})}\n\n"
        )

        final_state = initial_state.copy()

        try:
            for event in workflow.stream(initial_state):
                for node_name, state_update in event.items():
                    final_state.update(state_update)

                    # Prepare summary data to keep SSE messages lean and fast
                    event_data = {
                        "event_type": "node_update",
                        "session_id": session_id,
                        "node": node_name,
                        "update": state_update,
                    }

                    yield (
                        f"event: node_update\n"
                        f"data: {json.dumps(event_data, default=str)}\n\n"
                    )

            # Refreshed session status
            refreshed = get_session(session_id)
            end_status = refreshed.status if refreshed else "completed"

            yield (
                f"event: complete\n"
                f"data: {json.dumps({'event_type': 'complete', 'session_id': session_id, 'status': end_status})}\n\n"
            )

        except Exception as e:
            update_session(session_id, status="failed")
            yield (
                f"event: error\n"
                f"data: {json.dumps({'event_type': 'error', 'session_id': session_id, 'message': str(e)})}\n\n"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


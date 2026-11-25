import json
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    app: str = "PodResearch Agent"
    version: str = "1.0.0"


class SessionCreate(BaseModel):
    title: str = Field(..., description="Title or name of the podcast session")
    podcast_url: str = Field(..., description="YouTube URL of the podcast episode")


class SessionUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Updated session title")
    status: Optional[str] = Field(None, description="Updated session status")


class SessionResponse(BaseModel):
    id: str
    title: str
    podcast_url: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ArtifactResponse(BaseModel):
    id: str
    session_id: str
    artifact_type: str
    content: str
    created_at: datetime
    data: Optional[Any] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_parsed_data(cls, artifact: Any) -> "ArtifactResponse":
        parsed = None
        if artifact.content:
            try:
                parsed = json.loads(artifact.content)
            except (json.JSONDecodeError, TypeError):
                parsed = None

        return cls(
            id=artifact.id,
            session_id=artifact.session_id,
            artifact_type=artifact.artifact_type,
            content=artifact.content,
            created_at=artifact.created_at,
            data=parsed,
        )


class SessionDetailResponse(BaseModel):
    session: SessionResponse
    artifacts: list[ArtifactResponse]


class RunWorkflowRequest(BaseModel):
    resume: bool = Field(
        default=True,
        description="Whether to resume from existing cached artifacts in session memory"
    )


class RunWorkflowResponse(BaseModel):
    session_id: str
    status: str
    message: str
    final_state: Optional[dict[str, Any]] = None


class StreamEventData(BaseModel):
    event_type: str = Field(..., description="Type of event: start, node_update, complete, error")
    session_id: str
    node: Optional[str] = None
    data: Optional[Any] = None
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    
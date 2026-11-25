import os
import json
from typing import Any, Generator, Optional
import httpx


DEFAULT_BASE_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")


class PodResearchClient:
    """Client for interacting with the PodResearch FastAPI backend."""

    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def is_healthy(self) -> bool:
        """Check if FastAPI backend is healthy and responding."""
        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(f"{self.base_url}/health")
                return res.status_code == 200
        except Exception:
            return False

    def list_sessions(self) -> list[dict[str, Any]]:
        with httpx.Client(timeout=self.timeout) as client:
            res = client.get(f"{self.base_url}/api/sessions")
            res.raise_for_status()
            return res.json()

    def get_session(self, session_id: str) -> dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            res = client.get(f"{self.base_url}/api/sessions/{session_id}")
            res.raise_for_status()
            return res.json()

    def create_session(self, title: str, podcast_url: str) -> dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(
                f"{self.base_url}/api/sessions",
                json={"title": title, "podcast_url": podcast_url},
            )
            res.raise_for_status()
            return res.json()

    def delete_session(self, session_id: str) -> bool:
        with httpx.Client(timeout=self.timeout) as client:
            res = client.delete(f"{self.base_url}/api/sessions/{session_id}")
            return res.status_code == 204

    def get_latest_artifact(
        self, session_id: str, artifact_type: str
    ) -> Optional[dict[str, Any]]:
        with httpx.Client(timeout=self.timeout) as client:
            res = client.get(
                f"{self.base_url}/api/sessions/{session_id}/artifacts/{artifact_type}"
            )
            if res.status_code == 404:
                return None
            res.raise_for_status()
            return res.json()

    def stream_workflow(
        self, session_id: str
    ) -> Generator[dict[str, Any], None, None]:
        """Stream events from the backend via Server-Sent Events (SSE)."""
        url = f"{self.base_url}/api/sessions/{session_id}/stream"

        with httpx.stream("GET", url, timeout=None) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                if line.startswith("data: "):
                    raw_data = line[len("data: ") :]
                    try:
                        event = json.loads(raw_data)
                        yield event
                    except json.JSONDecodeError:
                        continue


import json
import sqlite3
import os
from typing import Dict, Any, Optional, List
from datetime import datetime


class SessionStore:
    """Thread-safe SQLite persistent store for research sessions and article history."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "sessions.db")

        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    podcast_url TEXT NOT NULL,
                    video_title TEXT,
                    video_description TEXT,
                    status TEXT NOT NULL,
                    transcript TEXT,
                    chunks_json TEXT,
                    outline_json TEXT,
                    article_json TEXT,
                    review_json TEXT,
                    history_json TEXT,
                    final_article TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            conn.commit()

    def save_session(
        self,
        session_id: str,
        podcast_url: str,
        video_title: Optional[str] = None,
        video_description: Optional[str] = None,
        status: str = "created",
        transcript: Optional[str] = None,
        chunks: Optional[List[dict]] = None,
        outline: Optional[dict] = None,
        article: Optional[dict] = None,
        review: Optional[dict] = None,
        history: Optional[List[dict]] = None,
        final_article: Optional[str] = None,
    ):
        now = datetime.utcnow().isoformat()
        with self._get_connection() as conn:
            existing = conn.execute(
                "SELECT session_id, history_json FROM sessions WHERE session_id = ?",
                (session_id,)
            ).fetchone()

            if existing:
                conn.execute("""
                    UPDATE sessions SET
                        podcast_url = COALESCE(?, podcast_url),
                        video_title = COALESCE(?, video_title),
                        video_description = COALESCE(?, video_description),
                        status = ?,
                        transcript = COALESCE(?, transcript),
                        chunks_json = COALESCE(?, chunks_json),
                        outline_json = COALESCE(?, outline_json),
                        article_json = COALESCE(?, article_json),
                        review_json = COALESCE(?, review_json),
                        history_json = COALESCE(?, history_json),
                        final_article = COALESCE(?, final_article),
                        updated_at = ?
                    WHERE session_id = ?
                """, (
                    podcast_url,
                    video_title,
                    video_description,
                    status,
                    transcript,
                    json.dumps(chunks) if chunks is not None else None,
                    json.dumps(outline) if outline is not None else None,
                    json.dumps(article) if article is not None else None,
                    json.dumps(review) if review is not None else None,
                    json.dumps(history) if history is not None else None,
                    final_article,
                    now,
                    session_id,
                ))
            else:
                conn.execute("""
                    INSERT INTO sessions (
                        session_id, podcast_url, video_title, video_description,
                        status, transcript, chunks_json, outline_json,
                        article_json, review_json, history_json, final_article,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    podcast_url,
                    video_title,
                    video_description,
                    status,
                    transcript,
                    json.dumps(chunks) if chunks is not None else None,
                    json.dumps(outline) if outline is not None else None,
                    json.dumps(article) if article is not None else None,
                    json.dumps(review) if review is not None else None,
                    json.dumps(history or []),
                    final_article,
                    now,
                    now,
                ))
            conn.commit()

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
            ).fetchone()
            if not row:
                return None

            return {
                "session_id": row["session_id"],
                "podcast_url": row["podcast_url"],
                "video_title": row["video_title"],
                "video_description": row["video_description"],
                "status": row["status"],
                "transcript": row["transcript"],
                "chunks": json.loads(row["chunks_json"]) if row["chunks_json"] else [],
                "outline": json.loads(row["outline_json"]) if row["outline_json"] else None,
                "article": json.loads(row["article_json"]) if row["article_json"] else None,
                "review": json.loads(row["review_json"]) if row["review_json"] else None,
                "history": json.loads(row["history_json"]) if row["history_json"] else [],
                "final_article": row["final_article"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }

    def list_sessions(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT session_id, podcast_url, video_title, status, created_at, updated_at FROM sessions ORDER BY updated_at DESC"
            ).fetchall()
            return [dict(r) for r in rows]


_global_store = None


def get_session_store() -> SessionStore:
    global _global_store
    if _global_store is None:
        _global_store = SessionStore()
    return _global_store
